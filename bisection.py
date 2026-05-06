"""
2-x^2

x-int = sqrt(2)
"""

def f(x):
    return 2-x**2

"""
for i from 1 to 3
"""
a=0
b=4
for i in [1,2,3,4,5,6]:
    c = (a+b)/2
    if f(a)*f(c)<0:
        b=c
    elif f(c)*f(b)<0:
        a=c
    else:
        print("I give up")
        break

print((a+b)/2)