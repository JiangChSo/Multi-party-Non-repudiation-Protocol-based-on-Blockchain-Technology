# -*- coding: utf-8 -*-
from functools import reduce
from FORMAT_CONVERSION import *
from RSA import *
from BIGPRIME_GENERATOR import get_prime
def egcd(a, b):
    """扩展欧几里得"""
    if 0 == b:
        return 1, 0, a
    x, y, q = egcd(b, a % b)
    x, y = y, (x - a // b * y)
    return x, y, q

def chinese_remainder(pairs):
    """中国剩余定理"""
    mod_list, remainder_list = [p[0] for p in pairs], [p[1] for p in pairs]
    mod_product = reduce(lambda x, y: x * y, mod_list)
    mi_list = [mod_product//x for x in mod_list]
    mi_inverse = [egcd(mi_list[i], mod_list[i])[0] for i in range(len(mi_list))]
    x = 0
    for i in range(len(remainder_list)):
        x += mi_list[i] * mi_inverse[i] * remainder_list[i]
        x %= mod_product
    return x

def key_process():
    f = open('key.txt')
    K = f.read()
    key_num = bin2dec(str2bin(K))
    return int(key_num)

def group_encryption():
    #密钥处理
    key_num = key_process()
    # 接收者 用户2 Bob的公钥和私钥
    (n1, e1, d1) = generate_key(50)
    print("(n,e,d) = "+str((n1, e1, d1)))
    print("公钥：" + str((n1, d1)))# 公钥
    print("私钥：" + str((n1, e1)))# 私钥
    cipher1 = fast_mod(key_num, e1, n1)# 加密
    print("生成的密文是: ", cipher1)
    plain_num1 = fast_mod(cipher1, d1, n1)  # 解密
    print("解密后的明文是: ", plain_num1)

    #接收者 用户3 Cindy的公钥和私钥
    (n2, e2, d2) = generate_key(50)
    print("(n,e,d) = "+str((n2, e2, d2)))
    print("公钥：" + str((n2, d2)))# 公钥
    print("私钥：" + str((n2, e2)))# 私钥
    cipher2 = fast_mod(key_num, e2, n2)# 加密
    print("生成的密文是: ", cipher2)
    plain_num2 = fast_mod(cipher2, d2, n2)  # 解密
    print("解密后的明文是: ", plain_num2)

    N1 = get_prime(51)#群加密中用户2的整数
    N2 = get_prime(51)#群加密中用户3的整数
    print(N1)
    print(N2)
    X = chinese_remainder([(N1,cipher1),(N2, cipher2)])#群加密密文
    print("群加密密文（中国剩余定理得到的结果）:"+str(X))

    #存储此次运行的N1，d1，n1和N2，d2，n2
    f = open(r"Publickey.txt","w")
    f.write(str(N1)+' '+str(d1)+' '+str(n1)+' '+
            str(N2) + ' ' + str(d2) + ' ' + str(n2))
    f.close()
    return X
    '''
    print(fast_mod(cipher1%N1, d1, n1))  # 用户1解密
    print(fast_mod(cipher2%N2, d2, n2))  # 用户2解密
    '''
