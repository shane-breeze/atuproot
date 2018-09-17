import uproot
import numpy as np
from numba import njit, int32, float32
from utils.Geometry import DeltaR2, RadToCart, CartToRad

np.random.seed(123456)

class JecVariations(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

        self.uncl_energy_thresh = 15.

        self.jesuncs = read_jesunc_file(self.jes_unc_file, overflow=True)
        self.jersfs = read_jersf_file(self.jer_sf_file, overflow=True)
        self.jers = read_jer_file(self.jer_file, overflow=True)

    def begin(self, event):
        self.isdata = event.config.dataset.isdata

    def event(self, event):
        if self.isdata:
            return True

        # JER
        jet_res = get_jet_ptresolution(
            self.jers, event.Jet, event.fixedGridRhoFastjetAll,
        )
        event.Jet_ptResolution = uproot.interp.jagged.JaggedArray(
            jet_res, event.Jet.starts, event.Jet.stops,
        )

        # Jet-GenJet matching
        jet_genjet_matchidx = match_jets_genjets(event.Jet, event.GenJet)
        event.Jet_genJetMatchIdx = uproot.interp.jagged.JaggedArray(
            jet_genjet_matchidx, event.Jet.starts, event.Jet.stops,
        )

        # JER correction
        jersf, jersf_up, jersf_down = get_jer_sfs(self.jersfs, event.Jet)
        jer_corr = get_jer_correction(jersf, event.Jet, event.GenJet)
        event.Jet_jerCorrection = uproot.interp.jagged.JaggedArray(
            jer_corr, event.Jet.starts, event.Jet.stops,
        )

        # Remove GenJets
        event.delete_branches(["GenJet_pt", "GenJet_eta", "GenJet_phi"])

        event.Jet.pt.content *= jer_corr
        event.Jet.mass.content *= jer_corr

        met, mephi = get_jer_met_correction(self.uncl_energy_thresh, jer_corr,
                                            event.Jet, event.MET)
        event.MET_pt = met
        event.MET_phi = mephi

        if self.variation is None:
            return True

        # JES
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

def get_jet_ptresolution(jers, jets, rho):
    """Function to modify arguments that are sent to a numba-jitted function"""
    return jit_get_jet_ptresolution(
        jers["bins"], jers["var_range"], jers["params"],
        jets.pt.content, jets.eta.content, jets.starts, jets.stops,
        rho,
    )

@njit
def jit_get_jet_ptresolution(bins, var_ranges, params,
                             jets_pt, jets_eta, jets_starts, jets_stops,
                             rho):
    resolution = np.zeros(jets_pt.shape[0], dtype=float32)
    for iev, (jb, je) in enumerate(zip(jets_starts, jets_stops)):
        for ij in range(jb, je):
            for ib in range(bins.shape[0]):
                within_eta = bins[ib][0] <= jets_eta[ij] < bins[ib][1]
                within_rho = bins[ib][2] <= rho[iev] < bins[ib][3]
                if within_eta and within_rho:
                    var_range = var_ranges[ib,:]
                    param = params[ib,:]

                    jet_pt = min(var_range[1], max(var_range[0], jets_pt[ij]))
                    resolution[ij] = np.sqrt(max(0.,
                        (param[0]*np.abs(param[0])/jet_pt**2) \
                        + param[1]**2*np.power(jet_pt, param[3]) \
                        + param[2]**2
                    ))
                    break
    return resolution

def match_jets_genjets(jets, genjets):
    """Function to modify arguments that are sent to a numba-jitted function"""
    return jit_match_jets_genjets(
        jets.pt.content, jets.eta.content, jets.phi.content, jets.ptResolution.content, jets.starts, jets.stops,
        genjets.pt.content, genjets.eta.content, genjets.phi.content, genjets.starts, genjets.stops,
    )

@njit
def jit_match_jets_genjets(jets_pt, jets_eta, jets_phi, jets_res, jets_starts, jets_stops,
                           genjets_pt, genjets_eta, genjets_phi, genjets_starts, genjets_stops):
    match_idx = -1*np.ones(jets_pt.shape[0], dtype=int32)
    for iev, (j_b, j_e, gj_b, gj_e) in enumerate(zip(jets_starts, jets_stops, genjets_starts, genjets_stops)):
        for ijs in range(j_b, j_e):
            for igjs in range(gj_b, gj_e):
                dr2 = DeltaR2(jets_eta[ijs]-genjets_eta[igjs],
                              jets_phi[ijs]-genjets_phi[igjs])
                within_dpt = np.abs(jets_pt[ijs]-genjets_pt[igjs]) < 3.*jets_res[ijs]*jets_pt[ijs]
                if dr2 < 0.04 and within_dpt:
                    match_idx[ijs] = igjs-gj_b
                    break
    return match_idx

def get_jer_sfs(jersfs, jets):
    """Function to modify arguments that are sent to a numba-jitted function"""
    return jit_get_jer_sfs(
        jersfs["bins"], jersfs["corrs"], jersfs["corrs_up"], jersfs["corrs_down"],
        jets.eta.content,
    )

@njit
def jit_get_jer_sfs(bins, corrs, corrs_up, corrs_down, jets_eta):
    sfs = np.ones(jets_eta.shape[0], dtype=float32)
    sfs_up = np.ones(jets_eta.shape[0], dtype=float32)
    sfs_down = np.ones(jets_eta.shape[0], dtype=float32)
    for ij in range(jets_eta.shape[0]):
        for ib in range(bins.shape[0]):
            within_eta = bins[ib,0] < jets_eta[ij] < bins[ib,1]
            if within_eta:
                sfs[ij] = corrs[ib]
                sfs_up[ij] = corrs_up[ib]
                sfs_down[ij] = corrs_down[ib]
                break
    return sfs, sfs_up, sfs_down

def get_jer_correction(jersf, jets, genjets):
    """Function to modify arguments that are sent to a numba-jitted function"""
    return jit_get_jer_correction(
        jersf,
        jets.pt.content, jets.genJetMatchIdx.content, jets.ptResolution.content,
        jets.starts, jets.stops,
        genjets.pt.content, genjets.starts, genjets.stops,
    )

@njit
def jit_get_jer_correction(jersf,
                           jets_pt, jets_genjetidx, jets_res, jets_starts, jets_stops,
                           genjets_pt, genjets_starts, genjets_stops):
    corrs = np.ones(jets_pt.shape[0], dtype=float32)
    for iev, (jb, je, gjb, gje) in enumerate(zip(jets_starts, jets_stops,
                                                 genjets_starts, genjets_stops)):
        for ij in range(jb, je):
            rel_genjetidx = jets_genjetidx[ij]
            if rel_genjetidx >= 0:
                corr = 1.+(jersf[ij]-1.)*(jets_pt[ij]-genjets_pt[gjb+rel_genjetidx])/jets_pt[ij]
            else:
                #corr = np.random.lognormal(0., jets_res[ij]*np.sqrt(max(jersf[ij]**2-1., 0.)))
                corr = np.random.normal(1., jets_res[ij]*np.sqrt(max(jersf[ij]**2-1., 0.)))
            #corrs[ij] = max(0., corr)
            corrs[ij] = np.abs(corr)
    return corrs

def get_jer_met_correction(uncl_energy_thresh, jer_corr, jets, met):
    return jit_get_jer_met_correction(
        uncl_energy_thresh, jer_corr,
        jets.pt.content, jets.phi.content, jets.starts, jets.stops,
        met.pt, met.phi,
    )

@njit
def jit_get_jer_met_correction(uncl_energy_thresh, jer_corr,
                               jets_pt, jets_phi, jets_starts, jets_stops,
                               met_pt, met_phi):
    met_out = np.zeros(met_pt.shape[0], dtype=float32)
    mephi_out = np.zeros(met_pt.shape[0], dtype=float32)
    for iev, (jb, je) in enumerate(zip(jets_starts, jets_stops)):
        mex, mey = RadToCart(met_pt[iev], met_phi[iev])
        for ij in range(jb, je):
            if jets_pt[ij] > uncl_energy_thresh:
                mex -= (1.-1./jer_corr[ij])*jets_pt[ij]*np.cos(jets_phi[ij])
                mey -= (1.-1./jer_corr[ij])*jets_pt[ij]*np.sin(jets_phi[ij])
        r, phi = CartToRad(mex, mey)
        met_out[iev] = r
        mephi_out[iev] = phi
    return met_out, mephi_out

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

def read_jesunc_file(filename, overflow=True):
    with open(filename, 'r') as f:
        lines = [l.strip().split() for l in f.read().splitlines()][1:]

    bins = np.array([map(float, l[:2]) for l in lines])
    xvals = np.array([[float(l[3*(1+idx)]) for idx in range(50)] for l in lines])
    yvals_up = np.array([[float(l[3*(1+idx)+1]) for idx in range(50)] for l in lines])
    yvals_down = np.array([[float(l[3*(1+idx)+2]) for idx in range(50)] for l in lines])

    if overflow:
        bins[0,0] = -np.infty
        bins[-1,-1] = np.infty

    return {
        "bins": bins,
        "xvals": xvals,
        "yvals_up": yvals_up,
        "yvals_down": yvals_down,
    }

def read_jersf_file(filename, overflow=True):
    with open(filename, 'r') as f:
        lines = [l.strip().split() for l in f.read().splitlines()][1:]

    bins = np.array([map(float, l[:2]) for l in lines])
    corrs = np.array([float(l[3]) for l in lines])
    corrs_up = np.array([float(l[5]) for l in lines])
    corrs_down = np.array([float(l[4]) for l in lines])

    if overflow:
        bins[0,0] = -np.infty
        bins[-1,-1] = np.infty

    return {
        "bins": bins,
        "corrs": corrs,
        "corrs_up": corrs_up,
        "corrs_down": corrs_down,
    }

def read_jer_file(filename, overflow=True):
    with open(filename, 'r') as f:
        lines = [l.strip().split() for l in f.read().splitlines()][1:]

    bins = np.array([map(float, l[:4]) for l in lines])
    var_range = np.array([map(float, l[5:7]) for l in lines])
    params = np.array([map(float, l[7:11]) for l in lines])

    if overflow:
        bins[:,0][np.where(bins[:,0] == bins[:,0].min())] = -np.infty
        bins[:,1][np.where(bins[:,1] == bins[:,1].max())] = np.infty
        bins[:,2][np.where(bins[:,2] == bins[:,2].min())] = 0.
        bins[:,3][np.where(bins[:,3] == bins[:,3].max())] = np.infty

    return {
        "bins": bins,
        "var_range": var_range,
        "params": params,
    }
