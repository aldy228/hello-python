# Parent class
class Person:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname

    def printname(self):
        print(self.firstname, self.lastname)


# Child class that uses parent's __init__ with super()
class Student(Person):
    def __init__(self, fname, lname, year):
        # Call Person.__init__ to set firstname and lastname
        super().__init__(fname, lname)
        # Add child-specific property
        self.graduationyear = year


# Create a Student and use inherited + new properties
s = Student("Mike", "Olsen", 2019)
s.printname()
print(s.graduationyear)  # 2019
