import numpy as np
from numba import njit, float32
from utils.Lambda import Lambda

class WeightQcdEwk(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def begin(self, event):
        self.parent = event.config.dataset.parent
        if self.parent not in self.input_paths:
            return

        self.lambda_formula = Lambda(self.formula)

        # {correction_name : (bin_min, bin_max, correction, errdown, errup)}
        self.input_dicts = {
            name: read_input(path, key)
            for name, (path, key) in self.input_paths[self.parent].items()
        }

    def end(self):
        self.lambda_formula = None

    def event(self, event):
        if self.parent not in self.input_paths:
            weights = np.ones(event.size)
        else:
            corrections = {
                name: get_corrections(event.GenPartBoson_pt, binmin, binmax, corr)
                for name, (binmin, binmax, corr, errdown, errup) in self.input_dicts.items()
            }
            weights = self.lambda_formula(**corrections)
        event.WeightQCDEWK = weights
        event.Weight_MET *= event.WeightQCDEWK
        event.Weight_SingleMuon *= event.WeightQCDEWK
        event.Weight_SingleElectron *= event.WeightQCDEWK

@njit
def get_corrections(boson_pts, bin_mins, bin_maxs, corrections):
    weights = np.zeros(boson_pts.shape[0], dtype=float32)
    for iev, boson_pt in enumerate(boson_pts):
        for ib, (bin_min, bin_max) in enumerate(zip(bin_mins, bin_maxs)):
            if bin_min <= boson_pt < bin_max:
                weights[iev] = corrections[ib]
                break
    return weights

def read_input(path, histname):
    with open(path, 'r') as f:
        lines = f.read().splitlines()

    start_idx = next(idx
                     for idx in range(len(lines))
                     if "# BEGIN HISTO1D {}".format(histname) in lines[idx])
    end_idx = next(idx
                   for idx in range(start_idx, len(lines))
                   if "# END HISTO1D" in lines[idx])

    data = np.array([map(float, l.split()) for l in lines[start_idx+2: end_idx]])

    bin_min, bin_max = data[:,0], data[:,1]
    correction = data[:,2]
    errdown, errup = data[:,3], data[:,4]

    return bin_min, bin_max, correction, errdown, errup
