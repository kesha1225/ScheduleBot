

def fact(n):
    res = 1
    for i in range(1, n + 1):
        res *= i
    return res


print(fact(5))
print(fact(6))
print(fact(7))
print(fact(8))
