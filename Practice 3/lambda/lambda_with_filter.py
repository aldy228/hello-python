# Lambda with filter(): keep items where condition is True
numbers = [1, 2, 3, 4, 5, 6, 7, 8]
odd_numbers = list(filter(lambda x: x % 2 != 0, numbers))   
print(odd_numbers)      # [1, 3, 5, 7]
