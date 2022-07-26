def call_function():
    a = 0
    b = callee()
    c = a + b
    d = a + callee()
    callee()
    f = a


def callee():
    return 5
