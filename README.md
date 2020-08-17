# Multi-party-Non-repudiation-Protocol-based-on-Blockchain-Technology

基于区块链技术的多方不可否认协议

多方不可否认协议在电子商务和电子邮件等领域都有重要的应用。已知的协议大多依赖可信第三方TTP，但TTP的中心化特性和对可靠性的高要求造成了协议的通信瓶颈。本文利用区块链去中心化特性设计了一种分发不同消息的自适应多方不可否认协议。本文给出了协议的基本假设和符号说明，展示了协议的具体流程，并实现了协议的关键部分，描述了设计决策与实现步骤。同时本文使用形式化分析方法证明出该协议满足公平性、不可否认性和时限性等安全性质，将协议与已有的两类多方不可否认协议进行性能对比，分析表明新协议效率得到一定程度的提高。

关键词：区块链；多方不可否认协议；形式化分析

本科毕业设计


运行前

确定安装了 Python 3.6+ (还有 pip) ，需要安装 Flask、 Requests 库，谷歌浏览器或Postman

##运行指南

打开控制台，开启第1个节点
```shell
$ python blockchain.py
```
打开二个控制台，开启第2个节点
```shell
$ python blockchain.py -p 5001
```
打开三个控制台，开启第3个节点
```shell
$ python blockchain.py -p 5002
```
打开第4个控制台，注册节点
```shell
$curl -X POST -H "Content-Type:application/json" -d'{"nodes":["http://127.0.0.1:5000"]}' http://127.0.0.1:5001/nodes/register
$curl -X POST -H "Content-Type:application/json" -d'{"nodes":["http://127.0.0.1:5000"]}' 
```
节点1（也可由其他节点执行）挖矿并提交交易http://localhost:5000/mine

节点1查看全部区块 http://localhost:5000/chain

节点2同步区块http://localhost:5001/nodes/resolve

节点3同步区块http://localhost:5002/nodes/resolve

节点2获取解密后的消息http://localhost:5001/message1/get

节点3获取解密后的消息http://localhost:5002/message2/get

Post请求操作
```shell
curl -X POST -H "Content-Type:application/json" -d'{"nodes":["http://127.0.0.1:5001"]}' http://127.0.0.1:5000/nodes/register
curl -X POST -H "Content-Type:application/json" -d'{"nodes":["http://127.0.0.1:5000"]}' http://127.0.0.1:5001/nodes/register
```

```
localhost:5000/nodes/resolve
http://localhost:5001/mine
http://localhost:5000/message1/get
http://localhost:5000/message2/get
```
