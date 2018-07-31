import numpy as np
from numba import njit, float32
from utils.Geometry import RadToCart, CartToRad, BoundPhi
from CollectionCreator import Collection

class EventSumsProducer(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def event(self, event):
        event.METnoX = Collection("METnoX", event)
        event.DiMuon = Collection("DiMuon", event)
        event.MHT40 = Collection("MHT40", event)

        # MET
        met, mephi = create_metnox(
            event.MET, event.MuonSelection, event.ElectronSelection,
        )
        event.METnoX_pt = met
        event.METnoX_phi = mephi

        # MET_dCaloMET
        met_dcalomet = np.abs(event.MET.pt - event.CaloMET.pt) / event.METnoX.pt
        event.MET_dCalMET = met_dcalomet

        # MET Resolution
        dimu_pt, dimu_phi, dimu_para, dimu_perp = create_metres(
            event.METnoX, event.MuonSelection,
        )
        event.DiMuon_pt = dimu_pt
        event.DiMuon_phi = dimu_phi
        event.METnoX_diMuonParaProjPt = dimu_para
        event.METnoX_diMuonPerpProjPt = dimu_perp

        # MHT
        ht, mht, mhphi = create_mht(
            event.JetSelectionClean,
        )
        event.HT40 = ht
        event.MHT40_pt = mht
        event.MHT40_phi = mhphi

        # dPhi(J, METnoX)
        jet_dphimet = create_jDPhiMETnoX(event.Jet, event.METnoX)
        event.Jet_dPhiMETnoX = jet_dphimet

def create_jDPhiMETnoX(jets, met):
    return create_jDPhiMETnoX_jit(met.phi, jets.phi.contents,
                                  jets.phi.starts, jets.phi.stops)

@njit(cache=True)
def create_jDPhiMETnoX_jit(mephi, jetphi, starts, stops):
    jet_dphis = np.zeros(jetphi.shape[0], dtype=float32)
    for iev, (start, stop) in enumerate(zip(starts, stops)):
        for jet_index in range(start, stop):
            jet_dphis[jet_index] = BoundPhi(jetphi[jet_index] - mephi[iev])
    return jet_dphis

def create_mht(jets):
    return create_mht_jit(jets.pt.contents, jets.phi.contents,
                          jets.pt.starts, jets.pt.stops)

@njit(cache=True)
def create_mht_jit(jetpt, jetphi, starts, stops):
    nev = stops.shape[0]
    hts = np.zeros(nev, dtype=float32)
    mhts = np.zeros(nev, dtype=float32)
    mhphis = np.zeros(nev, dtype=float32)

    for iev, (start, stop) in enumerate(zip(starts, stops)):
        ht, mhx, mhy = 0., 0., 0.
        for jet_index in range(start, stop):
            if jetpt[jet_index] > 40.:
                ht += jetpt[jet_index]
                px, py = RadToCart(jetpt[jet_index], jetphi[jet_index])
                mhx -= px
                mhy -= py
        hts[iev] = ht
        mhts[iev], mhphis[iev] = CartToRad(mhx, mhy)

    return hts, mhts, mhphis

def create_metres(metnox, muons):
    return create_metres_jit(metnox.pt, metnox.phi,
                             muons.pt.contents, muons.phi.contents,
                             muons.pt.starts, muons.pt.stops)

@njit(cache=True)
def create_metres_jit(met, mephi, mupt, muphi, mustarts, mustops):
    nev = met.shape[0]
    dimupts = np.zeros(nev, dtype=float32)
    dimuphis = np.zeros(nev, dtype=float32)
    metnox_dimuparas = np.zeros(nev, dtype=float32)
    metnox_dimuperps = np.zeros(nev, dtype=float32)

    for iev, (start, stop) in enumerate(zip(mustarts, mustops)):
        nmu = stop-start
        if nmu != 2:
            dimupt = np.nan
            dimuphi = np.nan
            metnox_dimupara = np.nan
            metnox_dimuperp = np.nan
        else:
            mux1, muy1 = RadToCart(mupt[start], muphi[start])
            mux2, muy2 = RadToCart(mupt[start+1], muphi[start+1])
            dimupt, dimuphi = CartToRad(mux1+mux2, muy1+muy2)

            dphi = BoundPhi(mephi[iev]-dimuphi)
            metnox_dimupara = met[iev]*np.cos(dphi)
            metnox_dimuperp = met[iev]*np.sin(dphi)

        dimupts[iev] = dimupt
        dimuphis[iev] = dimuphi
        metnox_dimuparas[iev] = metnox_dimupara
        metnox_dimuperps[iev] = metnox_dimuperp

    return dimupts, dimuphis, metnox_dimupara, metnox_dimuperp

def create_metnox(met, muons, electrons):
    return create_metnox_jit(met.pt,
                             met.phi,
                             muons.pt.contents,
                             muons.phi.contents,
                             muons.pt.starts,
                             muons.pt.stops,
                             electrons.pt.contents,
                             electrons.phi.contents,
                             electrons.pt.starts,
                             electrons.pt.stops)

@njit(cache=True)
def create_metnox_jit(met, mephi,
                      mupt, muphi, mustarts, mustops,
                      elpt, elphi, elstarts, elstops):
    nev = met.shape[0]
    mets_out = np.zeros(nev, dtype=float32)
    mephis_out = np.zeros(nev, dtype=float32)

    for iev, (musta, musto, elsta, elsto) in enumerate(zip(mustarts, mustops,
                                                           elstarts, elstops)):
        mex, mey = RadToCart(met[iev], mephi[iev])
        for muidx in range(musta, musto):
            mux, muy = RadToCart(mupt[muidx], mupt[muidx])
            mex, mey = mex+mux, mey+muy
        for elidx in range(elsta, elsto):
            elx, ely = RadToCart(elpt[elidx], elpt[elidx])
            mex, mey = mex+elx, mey+ely
        mets_out[iev], mephis_out[iev] = CartToRad(mex, mey)

    return mets_out, mephis_out
