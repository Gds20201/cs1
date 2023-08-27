import json

a = {1: {2: 3, 4: 5}}
b = a.items()
# print(b)
c = [x for x in a.items()]
print(c[0])
