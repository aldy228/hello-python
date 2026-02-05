a = 5
b = 2
if a > b: print("a is greater than b") # Short-hand if statement

a = 2
b = 330
print("A") if a > b else print("B") # Short-hand if-else statement

a = 10
b = 20
bigger = a if a > b else b
print("Bigger is", bigger) # Using short-hand if-else in an expression

a = 330
b = 330
print("A") if a > b else print("=") if a == b else print("B") # Short-hand if-elif-else statement

x = 15
y = 20
max_value = x if x > y else y
print("Maximum value:", max_value) # Assigning max value using short-hand if-else

username = ""
display_name = username if username else "Guest"
print("Welcome,", display_name) # Default value using short-hand if-else