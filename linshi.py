
import json
from filelock import FileLock


real2virtual = {}
virtual2real = {}
while 1:
    try:
        with FileLock("real2virtual.json.lock"):
            with open('real2virtual.json', 'r') as f:
                real2virtual = json.load(f)
        break
    except FileNotFoundError:
        print("real2virtual.json is Occupied")
print(real2virtual)
print(type(real2virtual))
for key, value in real2virtual.items():
    virtual2real[value] = key
