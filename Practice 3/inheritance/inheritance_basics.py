# Parent class
class Person:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname

    def printname(self):
        print(self.firstname, self.lastname)


# Use Person directly
x = Person("John", "Doe")
x.printname()


# Child class inherits from Person
class Student(Person):
    # 'pass' means: no extra properties/methods (yet)
    pass


# Student has everything Person has
s = Student("Mike", "Olsen")
s.printname()
