MyRHM1.0  
实现了IP数据包在转发过程中，将真实IP替换为虚拟IP  
暂未实现IP的定时突变功能  

MyRHM2.0

目前实现了IP的定时突变功能，但是未解决由于IP突变导致的数据包丢失问题
  
#### 主要工程文件：  
const.py - 用于存储常量  
CreateTopo.py - 用于创建mininet虚拟网络  
ryu.py - 用于操作控制器  

#### 运行方式：  
在终端1运行以下指令:  
./start_mininet.sh  
在终端2运行以下指令：  
ryu-manager ryu.py
