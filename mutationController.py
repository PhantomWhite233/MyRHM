from filelock import FileLock
import const
import random
import json
import time

real_ips = const.REAL_IPS
virtual_ips = const.VIRTUAL_IPS

# 初始化真实ip和虚拟ip的映射，后续只存储真实ip到虚拟ip的映射
real2virtual = {}  # 真实ip到虚拟ip的映射 
random_indexes = random.sample(range(0, len(virtual_ips)), const.BLOCK_SIZE)
for i in range(const.BLOCK_SIZE):
    real2virtual[real_ips[i]] = virtual_ips[random_indexes[i]]

# 创建并存储
real2virtual_json = json.dumps(real2virtual)
with FileLock("real2virtual.json.lock"):
    with open('real2virtual.json', 'w') as f:
        json.dump(real2virtual_json, f)

while 1:
    # 每次隔固定的时间间隔进行突变
    time.sleep(const.MUTATION_TIME)

    # 选定替换的虚拟ip
    random_indexes = random.sample(list(set(range(0, len(virtual_ips))) - set(random_indexes)), const.BLOCK_SIZE)
    real2virtual.clear()
    for i in range(const.BLOCK_SIZE):
        real2virtual[real_ips[i]] = virtual_ips[random_indexes[i]]

    # 存储
    real2virtual_json = json.dumps(real2virtual)
    while 1:
        try:
            with FileLock("real2virtual.json.lock"):
                with open('real2virtual.json', 'w') as f:
                    json.dump(real2virtual_json, f)
        except:
            print("real2virtual.json is Occupied")