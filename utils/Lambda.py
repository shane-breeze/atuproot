import numpy as np
np.warnings.filterwarnings('ignore')

class Lambda(object):
    def __init__(self, function):
        self.function = function

    def begin(self):
        self.lambda_function = eval('lambda '+self.function)

    def __call__(self, *event, **kwargs):
        if not hasattr(self, "lambda_function"):
            self.begin()
        try:
            return self.lambda_function(*event, **kwargs)
        except Exception as e:
            raise AttributeError(e, self.function)
