def my_function(fname):
    # fname is the parameter; value passed in is the argument
    print(fname + " Refsnes")


my_function("Emil")    # Emil Refsnes
my_function("Tobias")  # Tobias Refsnes


def from_country(country="Norway"):
    # If no argument is given, "Norway" is used
    print("I am from", country)


from_country("Sweden")
from_country()          # Uses default "Norway"

def pet_info(animal, name):
    print("I have a", animal, "named", name)


# Use parameter names when calling
pet_info(animal="dog", name="Buddy")
pet_info(name="Milo", animal="cat")   # Order can change with keywords


def print_fruits(fruits):
    # fruits is a list; loop through it
    for fruit in fruits:
        print(fruit)


my_fruits = ["apple", "banana", "cherry"]
print_fruits(my_fruits)


def add_two_numbers(x, y):
    # Send a result back to the caller
    return x + y


result = add_two_numbers(5, 3)
print(result)  # 8
