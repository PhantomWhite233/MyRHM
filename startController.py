import subprocess

# 启动第一个Python文件
p1 = subprocess.Popen(["ryu-manager", "ryu.py"])

# 启动第二个Python文件
p2 = subprocess.Popen(["python3", "mutationController.py"])

# 等待两个进程完成
p1.wait()
p2.wait()
