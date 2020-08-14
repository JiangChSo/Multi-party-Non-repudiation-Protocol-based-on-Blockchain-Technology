import hashlib
from DES import encrypt
import time
import json
from GROUP_ENCRYPTION_SCHEMES import group_encryption

def getkey():
    f = open('key.txt')
    return f.read()

def conk_p():
    M_1 = 'execute'
    M_2 = 'terminated'
    key = getkey()#获得对称密钥
    c_1 = encrypt(M_1, key)#对不同的消息进行加密
    c_2 = encrypt(M_2, key)
    # 存储此次运行的不同集合的消息密文，模拟用户提前通过信道接收
    f = open(r"cipher.txt", "w",encoding = 'utf-8')
    f.write(c_1+ '\n'+c_2)
    f.close()
    hc_1 = hashlib.sha256(c_1.encode()).hexdigest()  # h(c_1)
    hc_2 = hashlib.sha256(c_2.encode()).hexdigest()  # h(c_2)
    hk = hashlib.sha256(key.encode()).hexdigest()

    G_1 = ['Bob']  # 集合G1
    G_2 = ['Cindy']  # 集合G2
    l_m_1 = {
        'O': 'Alice',
        'G_i': G_1,
        'h(c_i)': hc_1,
        'h(k)': hk,
    }
    l_m_2 = {
        'O': 'Alice',
        'G_i': G_2,
        'h(c_i)': hc_2,
        'h(k)': hk,
    }
    print(l_m_1)
    print(l_m_2)
    # print(type(l_m_1)) 字典格式，不能有集合，不然无法json序列化
    # print(type(l_m_2))
    l_1 = json.dumps(l_m_1, sort_keys=True).encode('utf-8')
    l1 = hashlib.sha256(l_1).hexdigest()
    l_2 = json.dumps(l_m_2, sort_keys=True).encode('utf-8')
    l2 = hashlib.sha256(l_2).hexdigest()
    L_m = [l1, l2]
    #L_m_h = hashlib.sha256(str(L_m).encode('utf-8')).hexdigest()
    group_result = group_encryption()
	#构造密钥公布证据
    con_kp = {
        'identifying': "f_con",
        'O': "Alice",
        'R_m': "{Bob,Cindy}",
        'L\'': L_m,
        'h(k)': hk,
       # 't': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        't': time.time(),
        'E_R\'(k)': group_result
    }
    return con_kp