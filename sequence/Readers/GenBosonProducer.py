import numpy as np
from numba import njit, boolean, int32, float32
from . import Collection
from utils.Geometry import DeltaR2, LorTHPMToXYZE, LorXYZEToTHPM

class GenBosonProducer(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def event(self, event):
        mask = genpart_candidate_mask(event.GenPart.pdgId.content,
                                      event.GenPart.status.content,
                                      event.GenPart.statusFlags.content)
        event.GenPartBosonDaughters = Collection("GenPartBosonDaughters",
                                                 event, "GenPart", mask)

        event.nGenBosons = ngen_bosons(event.GenPart.pdgId.content,
                                       event.GenPart.genPartIdxMother.content,
                                       event.GenPart.starts,
                                       event.GenPart.stops)

        event.GenPartBosonDaughters.pdgId
        event.GenPartBosonDaughters.pt
        event.GenPartBosonDaughters.eta
        event.GenPartBosonDaughters.phi
        event.GenPartBosonDaughters.mass

        # Finished with GenPart branches
        event.delete_branches(["GenPart_pdgId",
                               "GenPart_status",
                               "GenPart_statusFlags",
                               "GenPart_pt",
                               "GenPart_eta",
                               "GenPart_phi",
                               "GenPart_mass",
                               "GenPart_genPartIdxMother"])

        genpart_dressedlepidx = genpart_matched_dressedlepton(
            event.GenPartBosonDaughters, event.GenDressedLepton,
        )
        event.GenPartBosonDaughters_genDressedLeptonIdx = genpart_dressedlepidx

        pt, eta, phi, mass = create_genpart_boson(event.GenPartBosonDaughters,
                                                  event.GenDressedLepton)
        event.GenPartBoson_pt = pt
        event.GenPartBoson_eta = eta
        event.GenPartBoson_phi = phi
        event.GenPartBoson_mass = mass

        event.delete_branches(["GenPartBosonDaughters_pdgId",
                               "GenPartBosonDaughters_pt",
                               "GenPartBosonDaughters_eta",
                               "GenPartBosonDaughters_phi",
                               "GenPartBosonDaughters_mass",
                               "GenPartBosonDaughters_genDressedLeptonIdx",
                               "GenPartBosonDaughters",
                               "GenDressedLepton_pdgId",
                               "GenDressedLepton_pt",
                               "GenDressedLepton_eta",
                               "GenDressedLepton_phi",
                               "GenDressedLepton_mass"])

def create_genpart_boson(genpart, gendressedlep):
    return create_genpart_boson_jit(genpart.pt.content,
                                    genpart.eta.content,
                                    genpart.phi.content,
                                    genpart.mass.content,
                                    genpart.genDressedLeptonIdx,
                                    genpart.pt.starts,
                                    genpart.pt.stops,
                                    gendressedlep.pt.content,
                                    gendressedlep.eta.content,
                                    gendressedlep.phi.content,
                                    gendressedlep.mass.content,
                                    gendressedlep.pt.starts,
                                    gendressedlep.pt.stops)

@njit
def create_genpart_boson_jit(gps_pt, gps_eta, gps_phi, gps_mass, gps_gdidx,
                             gps_starts, gps_stops,
                             gds_pt, gds_eta, gds_phi, gds_mass,
                             gds_starts, gds_stops):

    nev = gps_stops.shape[0]
    pts = np.zeros(nev, dtype=float32)
    etas = np.zeros(nev, dtype=float32)
    phis = np.zeros(nev, dtype=float32)
    masss = np.zeros(nev, dtype=float32)

    for iev, (gps_start, gps_stop, gds_start, gds_stop) in enumerate(zip(
        gps_starts, gps_stops, gds_starts, gds_stops,
    )):
        x, y, z, e = 0., 0., 0., 0.
        for igps in range(gps_start, gps_stop):
            igds = gps_gdidx[igps]
            if igds >= 0:
                igds += gds_start
                tx, ty, tz, te = LorTHPMToXYZE(
                    gds_pt[igds], gds_eta[igds], gds_phi[igds], gds_mass[igds],
                )
                x += tx
                y += ty
                z += tz
                e += te
            else:
                tx, ty, tz, te = LorTHPMToXYZE(
                    gps_pt[igps], gps_eta[igps], gps_phi[igps], gps_mass[igps],
                )
                x += tx
                y += ty
                z += tz
                e += te
        t, h, p, m = LorXYZEToTHPM(x, y, z, e)
        pts[iev] = t
        etas[iev] = h
        phis[iev] = p
        masss[iev] = m
    return pts, etas, phis, masss

def genpart_matched_dressedlepton(genparts, gendressedleps):
    return genpart_matched_dressedlepton_jit(genparts.pdgId.content,
                                             genparts.eta.content,
                                             genparts.phi.content,
                                             genparts.pdgId.starts,
                                             genparts.pdgId.stops,
                                             gendressedleps.pdgId.content,
                                             gendressedleps.eta.content,
                                             gendressedleps.phi.content,
                                             gendressedleps.pdgId.starts,
                                             gendressedleps.pdgId.stops)

@njit
def genpart_matched_dressedlepton_jit(gps_pdg, gps_eta, gps_phi,
                                      gps_starts, gps_stops,
                                      gds_pdg, gds_eta, gds_phi,
                                      gds_starts, gds_stops):
    indices = np.zeros(gps_pdg.shape[0], dtype=int32)
    for iev, (gps_start, gps_stop, gds_start, gds_stop) in enumerate(zip(
        gps_starts, gps_stops, gds_starts, gds_stops,
    )):
        for igps in range(gps_start, gps_stop):
            for igds in range(gds_start, gds_stop):
                if gps_pdg[igps] == gds_pdg[igds]:
                   if DeltaR2(gps_phi[igps]-gds_phi[igds],
                              gps_phi[igps]-gds_phi[igds]) < 0.01:
                        indices[igps] = igds - gds_start
                        break
            else:
                indices[igps] = -1
    return indices

@njit
def genpart_candidate_mask(pdgs, status, flags):
    mask = np.zeros(pdgs.shape[0], dtype=boolean)
    for ip in range(pdgs.shape[0]):
        if ((flags[ip]&1) and (flags[ip]&1<<8)) and (\
            (abs(pdgs[ip]) in [11, 13] and status[ip]==1 and not (flags[ip]&1<<2)) or\
            (abs(pdgs[ip])==15 and status[ip]==2) or\
            (abs(pdgs[ip]) in [12, 14, 16] and status[ip]==1)):
            mask[ip] = True
    return mask

@njit
def ngen_bosons(pdgs, mother_idxs, starts, stops):
    ngen_bosons = np.zeros(stops.shape[0], dtype=int32)
    for iev, (start, stop) in enumerate(zip(starts, stops)):
        value = 0
        for ip in range(start, stop):
            if abs(pdgs[ip]) in [11, 12, 13, 14, 15, 16, 23, 24] and mother_idxs[ip]==0:
                if abs(pdgs[ip])<20:
                    value += 1
                else:
                    value += 2
        ngen_bosons[iev] = value/2
    return ngen_bosons
