

n = int(input())

n_list = [int(input()) for _ in range(n)]


for j, i in enumerate(n_list, start=1):
    print(i ** j)
