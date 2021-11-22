import json
d = {
    "Number":"9900783185",
    "UniqueId" : "182823238"
}

print(d)

l = json.dumps(d)

x = bytes(l,'utf-8')
print(x)

y = x.decode('utf-8')

print(y)

r = json.loads(y)
print(r)