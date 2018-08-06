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

        mtw = create_mtw(met, muon, ele)
        event.MTW = mtw

        mll1 = create_mll(muon)
        mll2  = create_mll(ele)
        mll1[np.isnan(mll1)] = mll2[np.isnan(mll1)]
        event.MLL = mll1

def create_mll(leps):
    return create_mll_jit(leps.pt.content, leps.eta.content,
                          leps.phi.content, leps.mass.content,
                          leps.pt.starts, leps.pt.stops)

@njit
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
                          muon.pt.content, muon.phi.content,
                          muon.pt.starts, muon.pt.stops,
                          ele.pt.content, ele.phi.content,
                          ele.pt.starts, ele.pt.stops)

@njit
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

@njit
def calc_mtw(ptprod, dphi):
    return np.sqrt(2*ptprod*(1-np.cos(dphi)))
