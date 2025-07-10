"""
Day4- Python Programming

Collections

a=10
s="welcome"
d=10.5

List
Tuple
Set
Dictionary

List

A list is a collection which is ordered and changeable.
In Python lists are written with square brackets [ ].
List is mutable. (can be changed)

Tuple

A tuple is a collection which is ordered and unchangeable.
In Python tuples are written with round brackets. ()
Tuple is Immutable. (cannot be changed)

if it is Immutable below things are not possible....

1) we cannot modify existign value
2) we cannot append new valuel
3) we cannot insert a new value
4) we cannot remove a value

"""

"""

#Example1 :how to create list

# mylist1=[10,20,30,40, 50]
# mylist2=["apple", "banana", "cherry"]
# mylist3=["apple", 10, "banana", 20]
# mylist=list() # empty list
#
# print(mylist1)
# print(mylist2)
# print(mylist3)
# print(mylist)

#Example2: Accessing items from the list
mylist=["apple", "banana", "cherry"] #index starts from O

print(mylist[0]) # apple
print(mylist[2]) # cherry
print(mylist[-1]) # cherry
print(mylist[-2]) # banana

#Example3: Range of indexes
mylist=["apple", "banana", "cherry", "orange", "kiwi", "melon", "mango"]
print(mylist{2:5]) #'cherry''orange'"kiwi']

#Example4: change item value
# mylist=["apple", "banana", "cherry"]
# print(mylist) #['apple', 'banana', 'cherry']
# mylist[0]="orange" # this will change the values based on index
# print(mylist) ['orange', 'banana', 'cherry']

#Example5: read the list items using loop
# mylist=["apple", "banana", "cherry"]
# for i in mylist:
print (i)

"""
"""
#Examplr6: check if the item is exist in the list or not
mylist=["apple", "banana", "cherry"]

if "apple" in mylist:
    print("yes, apple is in the list")
else:
    print("no, apple is not in the list")

#Example7:List Length (counting number of items in a list
mylist=["apple", "banana", "cherry"]
print(len(mylist)) #3

#Example8: Add items append insert()
nylist=["apple", "banana", "cherry"]
nylist.append ("orange")
print(mylist)

#Example9: remove item from the list
#pop ()
mylist=["apple", "banana", "cherry"]
mylist.pop(0) # here we should specify index not the value
print(mylist) #['banana', 'cherry']

#del
# mylist=["apple", "banana", "cherry"]
# del mylist[2] #here del command removes single item based on the index
# print(mylist) #['apple', 'banana']

#clearO1
mylist=["apple", "banana", "cherry"]
del mylist[2] #here del command removes single item based on the index
print(mylist) #['apple'. 'banana' ]
"""

"""
#Example10: copy list
mylist1=["apple", "banana", "cherry"]
mylist2=list(mylist1) #copying the list
# mylist2=mylist1.copy() #copying the list

print(mylist1) #['apple', 'banana', 'cherry']
print(mylist2) #['apple', 'banana', 'cherry']

"""
"""
#Example11: join two lists
# can use + operator to join two lists or loop or extend() method
mylist1=["apple", "banana", "cherry"]
mylist2=["orange", "kiwi", "melon"]
mylist3=mylist1+mylist2 #joining two lists
print(mylist3) #['apple', 'banana', 'cherry', 'orange', 'kiwi', 'melon']

#using loop statement
for i in mylist2:
    mylist1.append(i)
print(mylist1) #['apple', 'banana', 'cherry', 'orange', 'kiwi', 'melon']

#using extend() method

mylist1.extend(mylist2) #joining two lists
print(mylist1) #['apple', 'banana', 'cherry', 'orange', 'kiwi', 'melon']

"""

#Example12: creating tuple
mytuple=("apple", "banana", "cherry")
print(mytuple[1]) #('apple', 'banana', 'cherry')
print(type(mytuple)) #<class 'tuple'>

#Example3: range of indexes
# mytuple=("apple", "banana", "cherry", "orange", "kiwi". ', "melon". , "mango")
# print(mytuple[2:5]) #('cherry', 'orange' ', 'kiwi')
# print(mytuple[-4:-1]) # ('orange', 'kiwi', 'melon')

#Example 4: Changing tuple items
# by default tuple does not allow you chnage values bcoz it is immutable
#but there is work around
#tuple--> list(modify)--> tuple

mytuple=("apple", "banana", "cherry")
mylist=list(mytuple)
mylist[0]="orange"
mytuple=tuple(mylist)
print(mytuple) #(orange', 'banana', 'cherry')

"""







"""







"""






"""


