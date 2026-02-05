fruits = ["apple", "banana", "cherry"]
for x in fruits:
  print(x)
  if x == "banana":
    break #with the break statement we can stop the loop even if there are more items

fruits = ["apple", "banana", "cherry"]
for x in fruits:
  if x == "banana":
    break #break comes before print
  print(x)