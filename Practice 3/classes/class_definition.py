# Basic class definition with a class attribute
class MyClass:
    x = 5  # class attribute (shared default)


# Create an object from the class
p1 = MyClass()
print(p1.x)  # 5


# Multiple objects from the same class
p2 = MyClass()
p3 = MyClass()

print(p1.x)  # 5
print(p2.x)  # 5
print(p3.x)  # 5


# Empty class using pass (placeholder)
class Person:
    pass  # keeps the class syntactically valid
