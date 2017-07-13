# import thread
# import time

# a = 10


# def test():
#     a = 11
#     print(a)


# thread.start_new_thread(test, ())
# print(a)

# time.sleep(1)
class A():
    def __del__(self):
        print "delete A"


def func():
    a = A()
    b = A()
    i = [2, ]

    def w():
        i[0] = i[0] - 1
        if i[0] <= 0:
            return a
    return w


f = func()
f()
f()
a = f()
del f
