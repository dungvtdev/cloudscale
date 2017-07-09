import thread
import time

a = 10


def test():
    a = 11
    print(a)


thread.start_new_thread(test, ())
print(a)

time.sleep(1)
