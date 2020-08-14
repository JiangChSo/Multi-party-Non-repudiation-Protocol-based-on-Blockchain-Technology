import re
# global definition
# base = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, A, B, C, D, E, F]
base = [str(x) for x in range(10)] + [ chr(x) for x in range(ord('A'),ord('A')+6)]

# bin2dec
# 二进制 to 十进制: int(str,n=10) 
def bin2dec(string_num):
 return str(int(string_num, 2))

# hex2dec
# 十六进制 to 十进制
def hex2dec(string_num):
 return str(int(string_num.upper(), 16))

# dec2bin
# 十进制 to 二进制: bin() 
def dec2bin(string_num):
 num = int(string_num)
 mid = []
 while True:
     if num == 0: break
     num,rem = divmod(num, 2)
     mid.append(base[rem])
 return ''.join([str(x) for x in mid[::-1]])

# dec2hex
# 十进制 to 八进制: oct() 
# 十进制 to 十六进制: hex() 
def dec2hex(string_num):
 num = int(string_num)
 mid = []
 while True:
    if num == 0: break
    num,rem = divmod(num, 16)
    mid.append(base[rem])
 return ''.join([str(x) for x in mid[::-1]])

# hex2tobin
# 十六进制 to 二进制: bin(int(str,16)) 
def hex2bin(string_num):
 return dec2bin(hex2dec(string_num.upper()))

# bin2hex
# 二进制 to 十六进制: hex(int(str,2)) 
def bin2hex(string_num):
 return dec2hex(bin2dec(string_num))

#字符串转化为二进制
def str2bin(message):
    res = ""
    for i in message:
        tmp = bin(ord(i))[2:]
        for j in range(0,8-len(tmp)):
            tmp = '0'+ tmp   #把输出的b给去掉
        res += tmp
    return res

#二进制转化为字符串
def bin2str(bin_str):
    res = ""
    tmp = re.findall(r'.{8}',bin_str)
    for i in tmp:
        res += chr(int(i,2))
    return res
    # print("未经过编码的加密结果:"+res)
    # print("经过base64编码:"+str(base64.b64encode(res.encode('utf-8')),'utf-8'))