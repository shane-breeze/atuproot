import json
import numpy as np
from numba import njit, boolean

class CertifiedLumiChecker(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def begin(self, event):
        self.runs, self.lumi_list = read_json(self.lumi_json_path)

    def event(self, event):
        event.IsCertified = is_certified_lumi(event.run, event.luminosityBlock,
                                              self.runs, self.lumi_list)

@njit
def is_certified_lumi(runs, lumis, cert_runs, cert_lumis):
    nev = runs.shape[0]
    is_certified = np.ones(nev, dtype=boolean)

    for iev in range(nev):
        # run not in list, skip
        passed = False
        for irun in range(cert_runs.shape[0]):
            if runs[iev] != cert_runs[irun]:
                continue

            cert_lumi_range = cert_lumis[irun]
            for ibin in range(cert_lumi_range.shape[0]):
                if cert_lumi_range[ibin,0] <= lumis[iev] <= cert_lumi_range[ibin,1]:
                    passed = True
                    break

            if passed:
                break
        is_certified[iev] = passed

    return is_certified

def read_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    runs = np.array(sorted(map(int, data.keys())))
    lumis = [np.array(data[str(r)], dtype=int) for r in runs]
    return runs, lumis
