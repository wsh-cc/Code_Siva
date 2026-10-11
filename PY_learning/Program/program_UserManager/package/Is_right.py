import re

def checkemail(mail):
    result = re.match(r'^[0-9a-zA-Z.-_]+@[a-zA-Z0-9.-_]+$', mail)
    if result:
        return 1
    else:
        return 0
    
def checkphone(phone):
    result =re.match(r"^[1-9][0-9]+$", phone)
    if result:
        return 1
    else:
        return 0
    
def checkage(age):
    result =re.match(r"^[1-9][0-9]+$", age)
    if result:
        return 1
    else:
        return 0