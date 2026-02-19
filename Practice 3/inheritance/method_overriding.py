# Parent class
class Person:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname

    def printname(self):
        print(self.firstname, self.lastname)


# Child adds more data and a new method
class Student(Person):
    def __init__(self, fname, lname, year):
        super().__init__(fname, lname)
        self.graduationyear = year

    def welcome(self):
        # New method only in Student
        print(
            "Welcome",
            self.firstname,
            self.lastname,
            "to the class of",
            self.graduationyear,
        )

    def printname(self):
        # Override parent's method (method overriding)
        print("Student:", self.firstname, self.lastname)


s = Student("Mike", "Olsen", 2019)
s.printname()   # Uses overridden version
s.welcome()
