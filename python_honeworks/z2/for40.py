a = int(input())
b = int(input())

for j, i in enumerate(range(a, b + 1), start=1):
    print(f"{i} " * j)
