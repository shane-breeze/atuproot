import numpy as np
#from numba import njit

class Lambda(object):
    def __init__(self, function):
        self.function = function

    def begin(self):
        self.lambda_function = eval('lambda '+self.function)

    def __call__(self, *event):
        if not hasattr(self, "lambda_function"):
            self.begin()
        return self.lambda_function(*event)
