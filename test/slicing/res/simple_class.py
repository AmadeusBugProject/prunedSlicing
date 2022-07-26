class MyTestClass:
    my_static_member = 3

    def __init__(self):
        MyTestClass.my_static_member = 5
        self.my_member = 1

    def my_method(self):
        self.my_member = self.my_member + 3


dummy = MyTestClass()
dummy.my_method()
