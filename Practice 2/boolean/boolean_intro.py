# Boolean values from variables
light_on = True
door_closed = False
if light_on:
    print("The light is on")
if not door_closed:
    print("The door is open")

# Boolean values from functions
def is_even(number):
    return number % 2 == 0  # Returns True or False
print(is_even(4))  # True
print(is_even(7))  # False