def debug(func):
    def inner(*args, **kwargs):
        print(func.__name__
              + " *args: " + str(*args)
              + ", **kwargs: " + str(**kwargs))
        result = func(*args, **kwargs)
        print(func.__name__ + " result: " + str(result))
        return result

    return inner
