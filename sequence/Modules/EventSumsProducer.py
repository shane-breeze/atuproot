import uproot
import numpy as np
from numba import njit, float32, int32
from utils.Geometry import RadToCart, CartToRad, BoundPhi
from .CollectionCreator import Collection

class EventSumsProducer(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def event(self, event):
        event.METnoX = Collection("METnoX", event)
        event.DiMuon = Collection("DiMuon", event)
        event.MHT40 = Collection("MHT40", event)
        event.LeadJetSelectionClean = Collection("LeadJetSelectionClean", event)

        # MET
        met, mephi = create_metnox(
            event.MET, event.MuonSelection, event.ElectronSelection,
        )
        event.METnoX_pt = met
        event.METnoX_phi = mephi

        # MET_dCaloMET
        met_dcalomet = np.abs(event.MET.pt - event.CaloMET.pt) / event.METnoX.pt
        event.MET_dCaloMET = met_dcalomet

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
        event.Jet_dPhiMETnoX = uproot.interp.jagged.JaggedArray(
            jet_dphimet, event.Jet.starts, event.Jet.stops,
        )

        event.MinDPhiJ1234METnoX = create_minDPhiJ1234METnoX(
            event.JetSelectionClean,
        )

        # nbjet
        event.nBJetSelectionCleanMedium = count_nbjet(
            event.JetSelectionClean.btagCSVV2.content,
            event.JetSelectionClean.starts,
            event.JetSelectionClean.stops,
            0.8484,
        )

        # Lead jet variables
        event.LeadJetSelectionClean_pt = create_lead_jet(
            event.JetSelectionClean.pt.content,
            event.JetSelectionClean.starts,
            event.JetSelectionClean.stops,
            pos = 0,
        )
        event.LeadJetSelectionClean_chHEF = create_lead_jet(
            event.JetSelectionClean.chHEF.content,
            event.JetSelectionClean.starts,
            event.JetSelectionClean.stops,
            pos = 0,
        )

@njit
def create_lead_jet(collection, starts, stops, pos=0):
    nev = stops.shape[0]
    collection_1d = np.zeros(nev, dtype=float32)
    for iev, (start, stop) in enumerate(zip(starts, stops)):
        if start+pos >= stop:
            collection_1d[iev] = np.nan
        else:
            collection_1d[iev] = collection[start+pos]
    return collection_1d

@njit
def count_nbjet(jet_btags, starts, stops, threshold):
    nev = stops.shape[0]
    nbjets = np.zeros(nev, dtype=int32)
    for iev, (start, stop) in enumerate(zip(starts, stops)):
        for ij in range(start, stop):
            if jet_btags[ij] > threshold:
                nbjets[iev] += 1
    return nbjets

def create_minDPhiJ1234METnoX(jets):
    return create_minDPhiJ1234METnoX_jit(jets.dPhiMETnoX.content,
                                         jets.starts,
                                         jets.stops)

@njit
def create_minDPhiJ1234METnoX_jit(jets_dphi, starts, stops):
    nev = stops.shape[0]
    mindphis = np.zeros(nev, dtype=float32)
    for iev, (start, stop) in enumerate(zip(starts, stops)):
        mindphi = 2*np.pi
        for ij in range(start, min(stop, start+4)):
            mindphi = min(mindphi, abs(jets_dphi[ij]))
        mindphis[iev] = mindphi
    return mindphis

def create_jDPhiMETnoX(jets, met):
    return create_jDPhiMETnoX_jit(met.phi, jets.phi.content,
                                  jets.phi.starts, jets.phi.stops)

@njit
def create_jDPhiMETnoX_jit(mephi, jetphi, starts, stops):
    jet_dphis = np.zeros(jetphi.shape[0], dtype=float32)
    for iev, (start, stop) in enumerate(zip(starts, stops)):
        for jet_index in range(start, stop):
            jet_dphis[jet_index] = BoundPhi(jetphi[jet_index] - mephi[iev])
    return jet_dphis

def create_mht(jets):
    return create_mht_jit(jets.pt.content, jets.phi.content,
                          jets.pt.starts, jets.pt.stops)

@njit
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
                             muons.pt.content, muons.phi.content,
                             muons.pt.starts, muons.pt.stops)

@njit
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
                             muons.pt.content,
                             muons.phi.content,
                             muons.pt.starts,
                             muons.pt.stops,
                             electrons.pt.content,
                             electrons.phi.content,
                             electrons.pt.starts,
                             electrons.pt.stops)

@njit
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
            mux, muy = RadToCart(mupt[muidx], muphi[muidx])
            mex, mey = mex+mux, mey+muy
        for elidx in range(elsta, elsto):
            elx, ely = RadToCart(elpt[elidx], elphi[elidx])
            mex, mey = mex+elx, mey+ely
        mets_out[iev], mephis_out[iev] = CartToRad(mex, mey)

    return mets_out, mephis_out
