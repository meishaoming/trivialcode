#!/usr/bin/env python

# import sys
#
# print('===============Python import mode=================')
# print('Command line:')
#
# for i in sys.argv:
#     print(i)
#
# print('\nPython path', sys.path)


# from sys import argv, path
#
# print('path:', path)


# a = b = c = 1
# print(a, b, c)
#
# a += 1
# print(a, b, c)

# a, b, c, d = 20, 5.5, True, 4+3j
# print(type(a))
# print(type(b))
# print(type(c))
# print(type(d))

class A:
    pass

class B(A):
    pass

print(isinstance(A(), A))
print(type(A()) == A)
print(isinstance(B(), A))
print(type(B()) == A)

