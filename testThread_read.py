import json
import time
from filelock import FileLock

def reader():
    while 1:
        try:
            with FileLock("shared_data.json.lock"):
                with open('shared_data.json', 'r') as f:
                    shared_data = json.load(f)  # 从JSON文件读取数据
                    num = int(input("是否保持读取"))
                    if num == 0:
                        return shared_data
                    elif num == 1:
                        continue
        except FileNotFoundError:
            print("shared_data.json not found.")


while 1:
    print("0-不读 1-读")
    num=int(input())
    if num == 0:
        continue
    elif num == 1:
        data = reader()
        print(data)