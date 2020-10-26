n = int(input())


def fib(i_):
    if i_ <= 2:
        return 1
    return fib(i_ - 2) + fib(i_ - 1)


i = 1

while fib(i) <= n:
    i += 1

print(fib(i))
