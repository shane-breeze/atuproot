import numpy as np

class SignalRegionBlinder(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def begin(self, event):
        self.isdata = event.config.dataset.isdata

    def event(self, event):
        if (self.isdata or self.apply_to_mc) and self.blind:
            event.BlindMask = (event.METnoX_pt <= 250.)
        else:
            event.BlindMask = np.ones(event.METnoX_pt.shape[0], dtype=bool)
