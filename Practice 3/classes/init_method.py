# Class with __init__ to set instance attributes
class Person:
    def __init__(self, name, age):
        # These are instance attributes, unique per object
        self.name = name
        self.age = age


# Create objects with different data
p1 = Person("John", 36)
p2 = Person("Mary", 25)

print(p1.name, p1.age)  # John 36
print(p2.name, p2.age)  # Mary 25

# You can delete an object explicitly
del p1  # after this, p1 no longer exists
