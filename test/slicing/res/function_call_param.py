def call_function():
    a = 1
    b = 2
    c = False
    d = True
    e = callee1(a, b)
    f = callee2(c, d)
    g = callee3(a, b, c)
    h = callee4(a, 1)
    i = c and d


# test int param
def callee1(x, y):
    return x > y


# test Boolean param
def callee2(x, y):
    return x and y


# test mixed param
def callee3(m,n,j):
    x = m > n
    y = j and x
    return y

# play with scope
def callee4(a, b):
    c = 1
    d = 0
    return a + b + c + d