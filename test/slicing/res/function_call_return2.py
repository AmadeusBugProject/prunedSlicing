def call_function():
    a = 0
    b = callee1()
    c = callee2()
    d = callee3()
    callee1()
    callee2()
    callee3()
    e = callee1() + callee2() + callee3()
    f = a + b + c + d


def callee1():
    a = 5
    return a


def callee2():
    a = 5
    return a + 2


def callee3():
    a = 0
    b = 3
    c = a + b
    return c
