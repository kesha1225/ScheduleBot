

n = int(input())

n_list = [(int(input()), int(input())) for _ in range(n)]


max_p = 0
index = None


for i, element in enumerate(n_list):
    m, v = element
    p = m / v
    if p > max_p:
        max_p = p
        index = i

print(max_p)
print(index + 1)
