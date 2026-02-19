class Flyer:
    def fly(self):
        print("I can fly")


class Walker:
    def walk(self):
        print("I can walk")


# Child class inherits from two parents
class Bird(Flyer, Walker):
    pass


b = Bird()
b.fly()   # from Flyer
b.walk()  # from Walker
