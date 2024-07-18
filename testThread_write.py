import json
import time
from filelock import FileLock

shared_data = {
    'key1': 'value1',
    'key2': 'value2'
}

while True:
    try:
        print("尝试读取")
        with FileLock("shared_data.json.lock"):
            with open('shared_data.json', 'w') as f:
                json.dump(shared_data, f, indent=4)  # 写入JSON文件，并设置缩进以便于阅读
        print("读取成功")
    except:
        print("other programme is reading data")
    print("Data written to shared_data.json")
    time.sleep(5)  # 每10秒写一次数据
