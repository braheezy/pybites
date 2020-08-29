#!venv/bin/python
from functools import reduce
x = [2, 3, 5, 7, 9]
y = [4, 5, 7, 10, 15]
N = len(x)

sum_x = sum(x)
sum_y = sum(y)

print(f'x sum: {sum_x}')
print(f'y sum: {sum_y}')

sum_x_y = sum(map(lambda pair: pair[0] * pair[1], zip(x, y)))
print(f'sum_x_y: {sum_x_y}')

sum_x_2 = sum(map(lambda n: n * n, x))
print(f'sum_x_2: {sum_x_2}')

print(f"N: {N}")

num = (N * sum_x_y) - (sum_x * sum_y)
den = (N * sum_x_2) - (sum_x * sum_x)
slope = num / den
print(f"m: {slope}")

b = (sum_y - (slope * sum_x)) / N
print(f'b: {b}')