
pure_matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

new_matrix = []

for row in list(reversed(pure_matrix)):
    new_matrix.append(list(reversed(row)))

print(new_matrix)



