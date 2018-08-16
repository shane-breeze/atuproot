import numpy as np
from numba import njit, int32

class LHEPartAssigner(object):
    old_parents = ["WJetsToLNu", "DYJetsToLL"]
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def event(self, event):
        if event.config.dataset.parent not in self.old_parents:
            return True

        event.LeptonDecay = get_lepton_id(event.LHEPart.pdgId.content,
                                          event.LHEPart.pdgId.starts,
                                          event.LHEPart.pdgId.stops)
        event.LeptonIsElectron = (event.LeptonDecay == 11)
        event.LeptonIsMuon = (event.LeptonDecay == 13)
        event.LeptonIsTau = (event.LeptonDecay == 15)

@njit
def get_lepton_id(pdgs, starts, stops):
    lepton_id = np.zeros(stops.shape[0], dtype=int32)
    for iev, (start, stop) in enumerate(zip(starts, stops)):
        for ilhe in range(start, stop):
            if abs(pdgs[ilhe]) in [11, 13, 15]:
                lepton_id[iev] = abs(pdgs[ilhe])
    return lepton_id
