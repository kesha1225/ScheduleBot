

pure_matrix = [
    [1, 2, -3],
    [4, 5, -6],
    [7, 8, -9]
]

new_matrix = []

for element in pure_matrix:
    new_el = element
    if element[-1] < 0:
        new_el = element[:-1]
    new_matrix.append(new_el)


print(new_matrix)

