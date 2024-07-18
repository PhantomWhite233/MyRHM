import subprocess

# 启动第一个Python文件
p1 = subprocess.Popen(["python", "testThread_write.py"])

# 启动第二个Python文件
p2 = subprocess.Popen(["python", "testThread_read.py"])

# 等待两个进程完成
p1.wait()
p2.wait()
