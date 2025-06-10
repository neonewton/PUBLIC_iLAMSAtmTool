# # range() : values between the range

# print(list(range(10))) #[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# print(list(range (5,10))) #[5, 6, 7,8,9]

# #print only odd numbers between 1-10
# print(list(range (1,10,2))) #[1, 3. 5. 7, 9]

# #print only even numbers between 1-10
# print(list(range (2,10,2))) #[2, 4, 6, 8]

# print(list(range (10,1, -1))) #[10, 9, 8, 7, 6, 5, 4, 3, 2]

# print(list(range(-10, -5))) # [-10, -9, -8, -7, -6]

"""
------------------------
conditional statements - if if..else
looping statements
jumping statements elif

print (1)
print (2)

range() function in python
------------------------
range (10) 0.....10
range (1,10) 1,........9
range (1,10,2) 1- starting point, 10 -ending point 2-increment

looping statemenets
------------------------
while loop
for loop

initilization
condition
incrementation
"""

"""
i=1

while i<=10:
    print(i)
    i+=1
print ("done!!")

for i in range (0,21,2):
    print(i)

for i in range (1,21,2):

break continue

"""
"""
for i in range (1,10):
    if i==5:
        break
    print (i) # 1....9
print("program exited!!!!")
"""
"""
# continue
for i in range (1,10):
    if 1==3 or 1==5 or 1==7:
        continue
    print (i)
print("program exited!!!!")

for i in range (3,7,2) :
    print (i)


# min() - returns miniumu value
print (min (10,20, 30,40,50,5,10,80, 100,40)) #5

print (max (10.5,20.5,5.5)) #20.5
print (min (10.5,20.5,5.5)) #20.5 
"""

"""
# create string varaible

#ways of creating string varialbes
s="welcome"
5= 'welcome'
s=str( 'welcome')
s=str ("welcome")

#creating empty string variables
name=""
name=' '
name=str(

# mutable - can change the value of the variable
# immutable - cannot change the value of variable
# string is immutable
"""

"""

str1 = "welcome"
print(id(str1)) #ID will varies

str2 = str1 + " to python "
print(id(str2)) #ID will varies

str3 = str2*3
print(id(str3)) #ID will varies
print(str3) #welcometopythonwelcometopythonwelcometopython

#Slicing operator

print(str1[1:3]) #print el meaning between starting element 1 to the element before element 3 ***
print(str1[:7]) #print welcome
print(str1[0:]) #welcome
print(str1[1:-1]) #elcom remove the last character of the string
"""

"""
# Example5: ord() and chr()
print(ord('A')) #65 # returns the ASCII code of the character.
print(chr (65)) #A #returns character represented by a ASCII number.

"""
"""
#Example6: max() min() len() 
print(max("abc")) #c
print(min("abc")) #a
print(len("abc")) #3

#Example 7: in not in operators~ returns true/false
s="welcome"
print("come" in s) #True
print ("lome" in s) #False

print("come" not in s) #True
print ("lome" not in s) #False

#Example8: String comparison
print("tim" == "tie") #False
print("free" != "freedom"). #True
print ("arrow" > "aron")_ #True
print ("right" >= "left") #True
print ("teeth" < "tee")_ #False
print ("yellow" <= "fellow") #False
print ("abc" > "") #True
"""

"""
# Example9 : Testing strings True/False
s = "welcome to python"

print(s.isalnum)) #False
print ("Welcome" isalpha())_ #True

print("2012" isdigit()) #True

print("first Number".isidentifier())#False

print(s.islower))_ #True
print(s.isupper()_ #True

print(" ".isspace()) #True

"""
"""
#Example10: Searching for Substrings
s = "welcome to python" 
print(s.endswith("thon")) #True

print(s.startswith("good")) #False

print(s.find("come")) #3
print(s.find("become")) #-1 not found

print(s.count("t")) #2. #Returns number of occurrences of substring the string
"""

"""
#ExampLe11: Converting String
s = "String in PYTHON"
s1 = s. capitalize
print(s1) #String in python

s2 = s.title()
print(s2)#String In Python

153 = s.lower()
print(s3) #string in python

s4 = s.upper()
print (s4) #STRING IN PYTHON

s5 = s. swapcase()
print(s5) #STRING IN python

s6 = s. replace("in", "on")
print(s6) #String on PYTHON

"""

"""
#ExampLe12: Reverse a string
#Method1
s="welcome"
rev_str="" #in order to store the reversed string for every iteration
for i in s:
    rev_str=i+rev_str
print("reversed string is:",rev_str) #emoclew
 

#Method2
s="welcome"
rev_str=s[::-1] # s[0:7:-1] #grab from the end to the beginning
print("reversed string is:",rev_str) #emoclew

"""