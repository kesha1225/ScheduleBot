a = [5, 6, 3, 2, 7, 8, 11, 3, 6, 87, 3, 2]

k = int(input())

mda = list(filter(lambda num: num[0] % k == 0, list(enumerate(a, start=1))))

for shue in mda:
    print(shue[1])

