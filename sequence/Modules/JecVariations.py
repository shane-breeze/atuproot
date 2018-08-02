import numpy as np
from numba import njit, int32

class JecVariations(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

        if self.variation is None:
            return

        self.bins, self.xvals, self.yvals_up, self.yvals_down = read_file(
            self.jes_unc_file, overflow=True,
        )

    def event(self, event):
        if self.variation is None:
            return True

        if self.variation == "up":
            yvals = self.yvals_up
            delta = 1.
        else:
            yvals = self.yvals_down
            delta = -1.

        bin_indices = select_bins(event.Jet.eta.content,
                                  self.bins)
        corrs = get_correction(event.Jet.pt.content,
                               bin_indices,
                               self.xvals,
                               yvals,
                               delta)

        event.Jet.pt.content *= corrs
        event.Jet.mass.content *= corrs

@njit
def interp(x, xp, fp):
    nx = xp.shape[0]

    if x < xp[0]:
        return fp[0]
    elif x > xp[-1]:
        return fp[-1]

    for ix in range(nx-1):
        if xp[ix] < x < xp[ix+1]:
            return (x - xp[ix]) * (fp[ix+1] - fp[ix]) / (xp[ix+1] - xp[ix]) + fp[ix]
    return np.nan

@njit
def get_correction(jvals, bin_indices, xvals, yvals, delta):
    njs = jvals.shape[0]
    corr = np.ones(njs)
    for ij in range(njs):
        val = jvals[ij]
        bin_idx = bin_indices[ij]
        corr[ij] = max(0., 1.+delta*interp(val,
                                           xvals[bin_idx],
                                           yvals[bin_idx]))
    return corr

@njit
def select_bins(vals, bins):
    njs = vals.shape[0]
    nbins = bins.shape[0]
    indices = np.zeros(njs, dtype=int32)
    for ij in range(njs):
        val = vals[ij]
        for ib in range(nbins):
            bin_= bins[ib,:]
            if bin_[0] < val < bin_[1]:
                indices[ij] = ib
                break
        else:
            indices[ij] = np.nan
    return indices

def read_file(filename, overflow=True):
    with open(filename, 'r') as f:
        lines = [l.strip().split() for l in f.read().splitlines()][1:]

    bins = np.array([map(float, l[:2]) for l in lines])
    xvals = np.array([[float(l[3*(1+idx)]) for idx in range(50)] for l in lines])
    yvals_up = np.array([[float(l[3*(1+idx)+1]) for idx in range(50)] for l in lines])
    yvals_down = np.array([[float(l[3*(1+idx)+2]) for idx in range(50)] for l in lines])

    if overflow:
        bins[0,0] = -np.infty
        bins[-1,-1] = np.infty

    return bins, xvals, yvals_up, yvals_down
