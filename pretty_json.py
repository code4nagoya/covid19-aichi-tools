import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print(json.dumps(json.loads(sys.stdin.read()), indent=4, ensure_ascii=False))

