b = int(input())

c = int(input())

lst = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]


for num in reversed(list(range(b, c + 1))):
    if num in lst:
        print(num)
        break
else:
    print(0, 0)
