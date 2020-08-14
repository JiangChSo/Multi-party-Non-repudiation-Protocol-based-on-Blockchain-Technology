import hashlib
import json
import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request
from CONK_P import conk_p
from RSA import fast_mod
from FORMAT_CONVERSION import dec2bin,bin2str
from DES import decode
from SIGNATURE import signature,verify

import base64

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        # 创建创世区块
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        """
        在节点列表中添加节点
        :param address: 节点地址. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def valid_chain(self, chain):
        """
        检验给定的链是否合法
        :param chain: 一个区块链
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            #检查区块hash是否正确
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            #检查工作量证明是否正确
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        共识算法解决冲突
        使用网络中最长的链
        :return: <bool> True如果链被取代，否则为False
        """

        neighbours = self.nodes
        new_chain = None

        # 最长的链长度
        max_length = len(self.chain)

        # 抓取并验证网络中所有节点的链
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # 检查链的长度是否更长，链是否合法
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # 如果发现了新的合法的更长的链就用它替换现有的链
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash):
        """
        生成一个新块，添加进链
        :param proof: <int> 工作量算法给出的工作量证明
        :param previous_hash: (optional) <str> 前一个块的哈希值
        :return: <dict> 新块
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # 重置交易池
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        生成新交易信息，交易将加入到下一个待挖的区块中
        :param sender: <str> 发送者地址
        :param recipient: <str> 接收者地址
        :param amount: <int> 交易额
        :return: <int>记录这笔交易的块的索引
        """
        con_kp = conk_p()
        con_k = signature(con_kp)
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'con_kp': con_kp,
            'signature_con_kp': str(con_k),
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        生成块的SHA-256 哈希值
        :param block: <dict> 块
        :return: <str> 哈希值
        """

        # 确定字典按键排序，保证哈希一致
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        工作量证明：
         - 查找一个p'使得hash(pp')以4个0开头
         - p是上一个块的proof，p’是当前的proof
        :param last_proof: <int>
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        验证证明：是否hash(last_proof, proof)以4个0开头

        :param last_proof: <int> 以前的证明
        :param proof: <int> 现在的证明
        :param last_hash: <str> 以前的区块hash
        :return: <bool> True if correct, False if not.

        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # 计算工作量证明
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # 给工作量证明的节点提供奖励
    # 发送者为0表示是新发出的币
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # 将新block加入chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # 检查交易结构要求的数据项齐全
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # 创建一笔新交易
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


@app.route('/message1/get', methods=['GET'])
def getmessage1():
    '''
    signature_con_kp1 =  blockchain.chain[-1]['transactions'][-1]['signature_con_kp']
    con_kp = blockchain.chain[-1]['transactions'][-1]['con_kp']
    signature_con_kp = signature(con_kp)#签名验证，防止伪造或篡改
    print(signature_con_kp1)
    verify(con_kp,signature_con_kp)
    '''
    group_encryption= blockchain.chain[-1]['transactions'][-1]['con_kp']['E_R\'(k)']
    print(group_encryption)
    f1 = open('Publickey.txt')
    PK = f1.read().split(' ')
    key_num = fast_mod(group_encryption % int(PK[0]), int(PK[1]), int(PK[2]))
    key = bin2str('0' + dec2bin(key_num))
    result = "Bob uses the public key to decrypt the group encrypted result: "+str(group_encryption)+", and get the Symmetric k: "+key+";\n"
    f2 = open('cipher.txt','r',encoding = 'utf-8')
    c = f2.read().split('\n')
    M1 = decode(c[0],key)
    result = result + "Bob uses the symmetric key k to decrypt the ciphertext c: "+c[0]+", and get the message: " + M1 +"."
    return result, 200

@app.route('/message2/get', methods=['GET'])
def getmessage2():
    group_encryption= blockchain.chain[-1]['transactions'][-1]['con_kp']['E_R\'(k)']
    print(group_encryption)
    f1 = open('Publickey.txt')
    PK = f1.read().split(' ')
    key_num = fast_mod(group_encryption % int(PK[3]), int(PK[4]), int(PK[5]))
    key = bin2str('0' + dec2bin(key_num))
    result = "Cindy利用公钥解密群加密结果E_R\'(k)："+str(group_encryption)+"，得到密钥k："+key+"；\n"
    f2 = open('cipher.txt','r',encoding = 'utf-8')
    c = f2.read().split('\n')
    M2 = decode(c[1],key)
    result = result + "Cindy利用对称密钥k解密密文c："+c[1]+"，得到消息M：" + M2
    return result, 200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')#参数解析
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
