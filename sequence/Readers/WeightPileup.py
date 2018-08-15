import numpy as np
from numba import njit, int32, float32

class WeightPileup(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def begin(self, event):
        with open(self.correction_file, 'r') as f:
            lines = [l.split() for l in f.read().splitlines()]
        self.bins = np.array([int(l[0]) for l in lines])
        self.correction = np.array([float(l[1]) for l in lines])
        self.correction_up = np.array([float(l[2]) for l in lines])
        self.correction_down = np.array([float(l[3]) for l in lines])

        if self.overflow:
            self.bins[-1] = 99999 #should be sufficiently large

    def event(self, event):
        indices = get_index(event.Pileup_nTrueInt.astype(int), self.bins)

        corr = get_correction(indices, self.correction)
        corr_up = get_correction(indices, self.correction_up) / corr
        corr_down = get_correction(indices, self.correction_down) / corr

        #event.Weight_pileup = corr
        event.Weight_pileupUp = corr_up
        event.Weight_pileupDown = corr_down

        event.Weight *= corr

@njit
def get_correction(indices, corrections):
    weights = np.ones(indices.shape[0], dtype=float32)
    for iev, idx in enumerate(indices):
        weights[iev] = corrections[idx]
    return weights

@njit
def get_index(vals, bins):
    indices = np.zeros(vals.shape[0], dtype=int32)
    for ival in range(vals.shape[0]):
        for ibin in range(bins.shape[0]-1):
            if bins[ibin] <= vals[ival] < bins[ibin+1]:
                indices[ival] = ibin
                break
        else:
            indices[ival] = -1
    return indices
