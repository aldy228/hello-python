# *args  -> any number of positional arguments (packed into a tuple)
# **kwargs -> any number of keyword arguments (packed into a dict)

def show_children(*kids): # *args: arbitrary positional arguments
    # kids is a tuple with all positional arguments
    print("All kids:", kids)
    print("Youngest child is", kids[-1])

show_children("Emil", "Tobias", "Linus")


def greet_all(greeting, *names):
    # greeting is normal argument, names are extra positional args
    for name in names:
        print(greeting, name)


greet_all("Hello", "Emil", "Tobias", "Linus")



def show_person(**person): #**kwargs: arbitrary keyword arguments
    # person is a dict with all keyword arguments
    print("All data:", person)
    print("Name:", person["name"])
    print("Age:", person["age"])


show_person(name="Tobias", age=30, city="Bergen")


# Regular argument + **kwargs
def show_user(username, **details):
    print("Username:", username)
    for key, value in details.items():
        print(" ", key + ":", value)


show_user("emil123", age=25, city="Oslo", hobby="coding")



def show_info(title, *args, **kwargs): #Both *args and **kwargs together 
    print("Title:", title)
    print("Positional args:", args)
    print("Keyword args:", kwargs)


show_info("User Info", "Emil", "Tobias", age=25, city="Oslo")


# ---------- Unpacking when calling ----------
def add_three(a, b, c):
    return a + b + c


nums = [1, 2, 3]
print(add_three(*nums))   # unpack list into a, b, c

person = {"fname": "Emil", "lname": "Refsnes"}
def hello(fname, lname):
    print("Hello", fname, lname)

hello(**person)           # unpack dict into keyword args
