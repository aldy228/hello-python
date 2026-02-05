print(10 > 9)
print(10 == 9)
print(10 < 9)
a = 200
b = 33

if b > a:
  print("b is greater than a")
else:
  print("b is not greater than a")
print(bool("Hello")) 
print(bool(15)) 

x = "Hello"
y = 15
print(bool(x))  
print(bool(y)) 

bool("abc") #Any string is True, except empty strings. Any number is True, except 0
bool(123)
bool(["apple", "cherry", "banana"])

bool(False) #In fact, there are not many values that evaluate to False, except: empty values such as ("", (), [], {}), the number 0, and the value None. And of course the value False evaluates to False.
bool(None) 
bool(0)
bool("")
bool(())    
bool([])
bool({})

class myclass():
  def __len__(self):
    return 0
myobj = myclass() #An object is considered True unless its class defines a __len__() function that returns 0 or a __bool__() function that returns False.
print(bool(myobj))

def myFunction() :
  return True
print(myFunction()) #function returns True

def myFunction() : 
  return True
if myFunction(): 
  print("YES!")
else:
  print("NO!")

x = 200
print(isinstance(x, int)) #check if x is integer type or not