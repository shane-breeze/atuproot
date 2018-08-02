import numpy as np
from numba import njit, float32

class WeightMetTrigger(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def begin(self, event):
        self.cats = sorted([nmu for nmu in self.correction_files.keys()])
        self.bins = []
        self.corr = []
        self.corr_up = []
        self.corr_down = []
        for nmuon in self.cats:
            bins, corr, corr_up, corr_down = read_file(self.correction_files[nmuon])
            self.bins.append(bins)
            self.corr.append(corr)
            self.corr_up.append(corr_up)
            self.corr_down.append(corr_down)

    def event(self, event):
        nmuons = event.MuonSelection.pt.stops - event.MuonSelection.pt.starts
        met = event.METnoX.pt
        corrs, corrs_up, corrs_down = get_correction(
            self.cats, self.bins, self.corr, self.corr_up, self.corr_down,
            nmuons, met,
        )
        event.Weight *= corrs
        event.Weight_metTrigSFUp = np.divide(corrs_up, corrs,
                                             out=np.zeros_like(corrs_up),
                                             where=corrs!=0)
        event.Weight_metTrigSFDown = np.divide(corrs_down, corrs,
                                               out=np.zeros_like(corrs_down),
                                               where=corrs!=0)

@njit
def get_correction(cats, bins, incorr, incorr_up, incorr_down, nmuons, met):
    nev = nmuons.shape[0]
    corrs = np.ones(nev, dtype=float32)
    corrs_up = np.ones(nev, dtype=float32)
    corrs_down = np.ones(nev, dtype=float32)

    for iev in range(nev):
        if nmuons[iev] not in cats:
            continue

        cat = cats.index(nmuons[iev])
        for ibin in range(bins[cat].shape[0]):
            if bins[cat][ibin,0] <= met[iev] < bins[cat][ibin,1]:
                corrs[iev] = incorr[cat][ibin]
                corrs_up[iev] = incorr_up[cat][ibin]
                corrs_down[iev] = incorr_down[cat][ibin]
                break
    return corrs, corrs_up, corrs_down

def read_file(path, overflow=True):
    with open(path, 'r') as f:
        lines = [l.split()
                 for l in f.read().splitlines()
                 if l.strip()[0]!="#"][1:]

    bins = np.array([map(float, l[1:3]) for l in lines])
    corr = np.array([float(l[3]) for l in lines])
    corr_up = np.array([1.+float(l[5]) for l in lines])
    corr_down = np.array([1.+float(l[4]) for l in lines])

    if overflow:
        bins[-1,-1] = np.infty

    return bins, corr, corr_up, corr_down
