def grouped_run(*args, **kwargs):
    return [arg[0](*arg[1]) for arg in args]
