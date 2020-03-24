import sys, json

print(json.dumps(json.loads(sys.stdin.read()), indent=4, ensure_ascii=False))

