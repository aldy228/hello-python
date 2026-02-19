# Class with a regular instance method
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def myfunc(self):
        # Use self to access instance data
        print("Hello, my name is " + self.name)


p1 = Person("John", 36)
p1.myfunc()  # calls the method on the object
