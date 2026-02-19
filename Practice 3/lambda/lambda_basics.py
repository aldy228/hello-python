# Basic lambda: one argument, one expression
add_10 = lambda a: a + 10
print(add_10(5))   # 15


# Multiple arguments
multiply = lambda a, b: a * b
print(multiply(5, 6))   # 30

sum3 = lambda a, b, c: a + b + c
print(sum3(5, 6, 2))    # 13


# Lambda inside another function
def myfunc(n):
    # Returns a lambda that multiplies by n
    return lambda a: a * n


mydoubler = myfunc(2)
print(mydoubler(11))    # 22

mytripler = myfunc(3)
print(mytripler(11))    # 33


# Using the same factory for both
mydoubler = myfunc(2)
mytripler = myfunc(3)
print(mydoubler(11))    # 22
print(mytripler(11))    # 33