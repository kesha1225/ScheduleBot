x = int(input())

n = int(input())

res = 0
for i in range(n):
    res += (-1) ** i * x ** (2 * i + 1) / (2 * i + 1)

print(res)
