def get_greeting():
    # Return a string instead of printing directly
    return "Hello from a function"


# Store the return value in a variable
message = get_greeting()
print(message)  # "Hello from a function"

# Use the return value directly
print(get_greeting())  # "Hello from a function"


# If you don't use 'return', the function returns None
def function_without_return():
    # Does something, but does not explicitly return a value
    print("I don't explicitly return anything.")


result = function_without_return()  # Prints message
print(result)  # None