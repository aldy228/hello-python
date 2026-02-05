temperature = 22
is_sunny = True
print(temperature > 20 and is_sunny)  
# True

# At least one condition must be True
has_wifi = False
has_mobile_data = True
print(has_wifi or has_mobile_data)  
# True

# Reverses the Boolean value
is_logged_in = False
print(not is_logged_in)  
# True

# Combining and, or, not
score = 85
passed_exam = True
print(score >= 60 and passed_exam)  
# True

# Using booleans in conditions
is_admin = False
if is_admin:
    print("Access granted")
else:
    print("Access denied")

print(bool(0))        # False
print(bool(1))        # True
print(bool(""))       # False
print(bool("Hello"))  # True
print(bool([]))       # False