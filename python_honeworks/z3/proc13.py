
def sort_dec3(a, b, c):
    a, b, c = sorted([a, b, c], reverse=True)
    return a, b, c


print(sort_dec3(3, 6, 1))
print(sort_dec3(44, 342234, 6546))
