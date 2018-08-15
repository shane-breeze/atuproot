import numpy as np

class WeightCreator(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def event(self, event):
        event.Weight = np.ones(event.size)
