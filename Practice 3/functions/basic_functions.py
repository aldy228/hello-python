# Creating a simple function
def my_function():
    # This code runs only when the function is called
    print("Hello from a function")


# Calling a function
my_function()  # Call the function once

# Calling the same function multiple times
my_function()
my_function()
my_function()


# Valid function names
def calculate_sum(a, b):
    # Returns the sum of two numbers
    return a + b


def _private_function():
    # By convention, leading underscore means "internal" helper
    print("This is a 'private' helper function")


def myFunction2():
    # CamelCase name – valid, but less common in Python
    print("CamelCase function name example")


# Using the functions above
print(calculate_sum(3, 4))  # 7
_private_function()         # "This is a 'private' helper function"
myFunction2()               # "CamelCase function name example"


# Without a function – the same formula repeated 3 times
temp1 = 77
celsius1 = (temp1 - 32) * 5 / 9
print(celsius1)  # Celsius for 77°F

temp2 = 95
celsius2 = (temp2 - 32) * 5 / 9
print(celsius2)  # Celsius for 95°F

temp3 = 50
celsius3 = (temp3 - 32) * 5 / 9
print(celsius3)  # Celsius for 50°F

# With a function – write the formula once, reuse it
def fahrenheit_to_celsius(fahrenheit):
    # Convert Fahrenheit to Celsius and return the result
    return (fahrenheit - 32) * 5 / 9

print(fahrenheit_to_celsius(77))  # Same as celsius1
print(fahrenheit_to_celsius(95))  # Same as celsius2
print(fahrenheit_to_celsius(50))  # Same as celsius3