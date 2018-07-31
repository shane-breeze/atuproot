import numpy as np
from numba import njit, float32
from utils.Geometry import LorTHPMToXYZE, LorXYZEToTHPM

class InvMassProducer(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def event(self, event):
        muon = event.MuonSelection
        ele = event.ElectronSelection
        met = event.MET

        event.MTW = create_mtw(met, muon, ele)
        MMuMu = create_mll(muon)
        MEE = create_mll(ele)
        MMuMu[np.isnan(MMuMu)] = MEE[np.isnan(MMuMu)]
        event.MLL = MMuMu

def create_mll(leps):
    return create_mll_jit(leps.pt.contents, leps.eta.contents,
                          leps.phi.contents, leps.mass.contents,
                          leps.pt.starts, leps.pt.stops)

@njit(cache=True)
def create_mll_jit(pt, eta, phi, mass, starts, stops):
    mlls = np.zeros(stops.shape[0], dtype=float32)
    for iev, (start, stop) in enumerate(zip(starts, stops)):
        nlep = stop - start
        if nlep == 2:
            px, py, pz, en = 0., 0., 0., 0.
            for muidx in range(start, stop):
                x, y, z, e = LorTHPMToXYZE(pt[muidx], eta[muidx], phi[muidx], mass[muidx])
                px += x
                py += y
                pz += z
                en += e
            t, h, p, m = LorXYZEToTHPM(px, py, pz, en)
            mlls[iev] = m
        else:
            mlls[iev] = np.nan
    return mlls

def create_mtw(met, muon, ele):
    return create_mtw_jit(met.pt, met.phi,
                          muon.pt.contents, muon.phi.contents,
                          muon.pt.starts, muon.pt.stops,
                          ele.pt.contents, ele.phi.contents,
                          ele.pt.starts, ele.pt.stops)

@njit(cache=True)
def create_mtw_jit(met,  mephi,
                   mupt, muphi, musta, musto,
                   elpt, elphi, elsta, elsto):
    mtws = np.zeros(met.shape[0], dtype=float32)
    for iev, (msta, msto, esta, esto) in enumerate(zip(musta, musto, elsta, elsto)):
        nmu = msto-msta
        nel = esta-esto

        mtw = np.nan
        if nmu == 1:
            mtw = calc_mtw(met[iev]*mupt[msta], mephi[iev]-muphi[msta])
        elif nel == 1:
            mtw = calc_mtw(met[iev]*elpt[esta], mephi[iev]-elphi[esta])
        mtws[iev] = mtw
    return mtws

@njit(cache=True)
def calc_mtw(ptprod, dphi):
    return np.sqrt(2*ptprod*(1-np.cos(dphi)))