# -*- coding: utf-8 -*-
import math
import random
"""
大素数生成方案选择Miller-Rabin检测,可以参考这篇文章：https://blog.csdn.net/qq_33828894/article/details/81358051
"""
#辗转相除法求最大公因数
def gcd(a, b):
    if a > b: a, b = b, a
    while b != 0:
        a, b = b, a%b
    return a

def isPrime(n):
    """
    判断一个数是否为素数
    厄拉托塞师除法
    """
    if n <= 1:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i== 0:
            return False
    return True

def generate_key(key_len): #key_len要比消息长度大
    """
    生成n, e, d
    """
    p = random_prime(key_len // 2)
    q = random_prime(key_len // 2)
    n  = p * q
    ph_n = (p -1) * (q -1)
    e = 65537 #e取固定值
    d = generate_d(ph_n, e)
    pbvk = (n ,e, d)
    return pbvk

#开始选择p q
def random_prime(half_len):
    while True:
        n = random.randint(0, 1 << half_len)#求2^half_len之间的大数
        if n % 2 != 0:
            found = True
            # 随机性测试
            for i in range(0, 5):   #5的时候错误率已经小于千分之一
                if prime_test(n) == False:
                    found = False
                    break
            if found == True:
                return n

#Miller-Rabin
def prime_test(n):
        """
        测试n是否为素数
        """
        q = n - 1
        k = 0
        # 寻找k,q 是否满足2^k*q =n - 1
        while q % 2 == 0:
            k += 1
            q = q // 2
        a = random.randint(2, n - 2)
        # 如果 a^q mod n= 1, n 可能是一个素数
        if fast_mod(a, q, n) == 1:
            return True
        # 如果存在j满足 a ^ ((2 ^ j) * q) mod n == n-1, n 可能是一个素数
        for j in range(0, k):
            if fast_mod(a, (2 ** j) * q, n) == n - 1:
                return True
        # n 不是素数
        return False

"""
运用了扩展欧几里的算法，求a*x + b*y = 1
递归条件:当m==0时，gcd(n,m)=n，此时x=1,y=0
"""
def ext_gcd(a, b):
    if b == 0:
        return 1, 0, a
    else:
        x, y, q = ext_gcd(b, a % b)
        x, y = y, (x - (a // b) * y)
        return x, y, q

def fast_mod(b, n, m):
    """
    快速幂
    """
    ret = 1
    tmp = b
    while n:
        if n & 0x1:
            ret = ret * tmp % m
        tmp = tmp * tmp % m
        n >>= 1
    return ret

#产生秘钥d
def generate_d(ph_n, e):
    (x, y, r) = ext_gcd(ph_n, e)
    # y maybe < 0, so convert it
    if y < 0:
        #return y % ph_n
        return y + ph_n  #直接用加法效率高一丢丢
    return y








