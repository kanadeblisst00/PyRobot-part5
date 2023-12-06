#### 目录修整

目前的系列目录(后面会根据实际情况变动):

1. [在windows11上编译python](https://mp.weixin.qq.com/s/nJq8XX203Wc_gwT5hSWYZA)
2. [将python注入到其他进程并运行](https://mp.weixin.qq.com/s/gvV9GRQZbvxHQSjfDieiqw)
3. [注入Python并使用ctypes主动调用进程内的函数和读取内存结构体](https://mp.weixin.qq.com/s/Dy8-nJPoXJp9_ZrrwOrC0w)
4. [调用汇编引擎实战发送文本和图片消息(同时支持32位和64位微信)](https://mp.weixin.qq.com/s/PJZDf5937SsncGU-RhZ3tA)
5. [允许Python加载运行py脚本且支持热加载](https://mp.weixin.qq.com/s/FWW1FecRo_yAhh9eLScAoA)
6. 利用汇编(keystone)和反汇编引擎(beaengine)写一个x86任意地址hook
7. 封装Detour写一个x64函数hook
8. 实战32位和64位接收消息和消息防撤回
9. 实战读取内存链表结构体(内存好友列表)
10. 根据bug反馈和建议进行细节上的优化
11. 做一个僵尸粉检测工具
12. 其他功能慢慢加

## 使用

打开微信后执行`main.py`会将Python注入到微信，然后实时监听该目录下的所有脚本变化。比如`robot.py`变化了就会重新加载并执行它

## 联系方式

现在对这个系列感兴趣人数较少，~~如果后面人多了会建个交流群~~，几个人也是人，hook接收消息那篇文章开始建群

想提建议或者占坑可以先加下好友：kanadeblisst