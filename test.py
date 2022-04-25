
class a:
    @profile
    def my_func(self):
        a = 1
        b = 1
        return a


def my_func1():
    a = 1
    b = 1
    return a


if __name__ == '__main__':
    a1 = a()
    a1.my_func()
    my_func1()


# python -m memory_profiler test.py
