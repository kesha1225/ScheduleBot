a = [2, 5, 1, 8, 34, 2, 32, 65, 9]


mda = reversed(list(filter(lambda num: num[0] % 2 != 0, list(enumerate(a, start=1)))))

for shue in mda:
    print(shue[1])
