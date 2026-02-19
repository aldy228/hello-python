# Showing shared class attribute vs instance attributes
class MyClass:
    x = 5  # class variable (same default for all objects)


p1 = MyClass()
p2 = MyClass()

print(p1.x)  # 5 (from class)
print(p2.x)  # 5 (from class)

# Changing on the instance creates/uses an instance attribute
p1.x = 10
print(p1.x)  # 10 (instance-specific now)
print(p2.x)  # still 5
