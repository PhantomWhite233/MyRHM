import json
import time
import filelock

shared_data = {
    'key1': 'value1',
    'key2': 'value2'
}

while True:
    try:
        print("try to writing...")
        with filelock("shared_data.json.lock"):
            with open('shared_data.json', 'w') as f:
                json.dump(shared_data, f, indent=4)  # 写入JSON文件，并设置缩进以便于阅读
        print("writing successfully")
    except:
        print("other programme is reading data")
    print("Data written to shared_data.json")
    time.sleep(5)  # 每10秒写一次数据
