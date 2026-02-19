# Lambda with map(): apply to every item
numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))
print(doubled)          # [2, 4, 6, 8, 10]