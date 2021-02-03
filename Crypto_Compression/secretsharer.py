'''
Created on Feb 1, 2019
@author: Andrew Gordon
'''
from fractions import Fraction
import random

if __name__ == '__main__':
    pass

'''
points = []
for i in range(2):
    points.append([])
    for j in range(2):
        points[i].append(0)
print(points)
'''

''' split is a function which is passed val,
 which is the secret(when x=0), n is the number
 of points to distribute, and k is the number
 of points needed to reconstruct the polynomial.
 Returns a list of n random points s.t. x!=0 for
 each point. '''


def split(val, n, k):
    '''make random polynomial'''
    coeffs = [0] + [Fraction(random.randint(1,100), random.randint(1,100)) for _ in range(k - 1)]
    coeffs[0] = val
    points = []
    for i in range(n):
        points.append([])
        points[i]=(i+1, (sum(coeff*(i+1)**n for n, coeff in enumerate(coeffs))))
    '''for (x, y) in points:
        print("x:", x, ", y:", y)
        for j in range(2):
            points[i].append(0)
    for i in range(n):
        points[i][0] = i + 1
        points[i][1] = sum(coeff * (i + 1) ** n for n, coeff in enumerate(coeffs))'''
    '''print("points:", points)
    print("coeffecients:", coeffs)
    print("val:", val)'''
    '''checks if x at 0 equals val with polynomial'''
    '''print(sum(coeff * 0**n for n, coeff in enumerate(coeffs)))'''
    '''return coeffs'''
    return points

''' interpolate is function where points is a list
of shares, x is the x-coordinate in which to compute
the secret. points is shares. Returns the computed secret value. '''


def interpolate(points, x):
    '''if (points.__len__())<4:
        return'''
    '''top = 1
    bottom = 1'''
    secret = 0
    j = 0
    for k in range(points.__len__()):
        top=1
        bottom=1
        for i in range(points.__len__()):
            if points[i][0] != points[j][0]:
                '''print(points[j][0], points[i][0])'''
                top = top * (x - points[i][0])
                bottom = bottom * (points[j][0] - points[i][0])
                '''print(points[j][0]-points[i][0], "j-i")'''
                '''print(top, "top",i, ",", bottom, "bottom")'''
        j = j + 1
        '''print(Fraction._div(top, bottom))'''
        secret = secret + (Fraction(top, bottom))*points[k][1]
        '''print("c",k,":",Fraction._div(top, bottom) * points[k][1])'''
    return secret

'''test = split(500000, 8, 7)
print("secret:",interpolate(test, 0))'''