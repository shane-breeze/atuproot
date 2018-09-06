import numpy as np

class WeightCreator(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def event(self, event):
        event.Weight_XsLumi = np.ones(event.size)
        event.Weight_MET = np.ones(event.size)
        event.Weight_SingleMuon = np.ones(event.size)
        event.Weight_SingleElectron = np.ones(event.size)
