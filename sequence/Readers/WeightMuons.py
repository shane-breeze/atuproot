import numpy as np
from numba import njit, float32

class WeightMuons(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def begin(self, event):
        # ID
        self.weights_id, self.corrections_id = zip(*[
            (w, read_file(path, form=["ptlow", "pthigh", "absetalow", "absetahigh", "corr", "unc"]))
            for w, path in self.correction_id_paths
        ])
        self.weights_id = np.array(self.weights_id)
        self.corrections_id = [
            [np.array(zip(*[sf.pop("ptlow"), sf.pop("pthigh")])),
             np.array(zip(*[sf.pop("absetalow"), sf.pop("absetahigh")])),
             np.array(sf["corr"]), np.array(sf["unc"]), np.array(sf.pop("unc"))]
            for sf in self.corrections_id
        ]
        for sf in self.corrections_id:
            sf[0][sf[0]==np.min(sf[0])] = 0.
            sf[0][sf[0]==np.max(sf[0])] = np.infty
            sf[1][sf[1]==np.min(sf[1])] = 0.
            sf[1][sf[1]==np.max(sf[1])] = np.infty

        # ISO
        self.weights_iso, self.corrections_iso = zip(*[
            (w, read_file(path, form=["ptlow", "pthigh", "absetalow", "absetahigh", "corr", "unc"]))
            for w, path in self.correction_iso_paths
        ])
        self.weights_iso = np.array(self.weights_iso)
        self.corrections_iso = [
            [np.array(zip(*[sf.pop("ptlow"), sf.pop("pthigh")])),
             np.array(zip(*[sf.pop("absetalow"), sf.pop("absetahigh")])),
             np.array(sf["corr"]), np.array(sf["unc"]), np.array(sf.pop("unc"))]
            for sf in self.corrections_iso
        ]
        for sf in self.corrections_iso:
            sf[0][sf[0]==np.min(sf[0])] = 0.
            sf[0][sf[0]==np.max(sf[0])] = np.infty
            sf[1][sf[1]==np.min(sf[1])] = 0.
            sf[1][sf[1]==np.max(sf[1])] = np.infty

        # Tracking
        self.weights_track, self.corrections_track = zip(*[
            (w, read_file(path, form=["etalow", "etahigh", "corr", "unc_down", "unc_up"]))
            for w, path in self.correction_track_paths
        ])
        self.weights_track = np.array(self.weights_track)
        self.corrections_track = [
            [np.array(zip(*[sf.pop("etalow"), sf.pop("etahigh")])),
             np.array(sf["corr"]), np.array(sf.pop("unc_up")), np.array(sf.pop("unc_down"))]
            for sf in self.corrections_track
        ]
        for sf in self.corrections_track:
            sf[0][sf[0]==np.min(sf[0])] = -np.infty
            sf[0][sf[0]==np.max(sf[0])] = np.infty

        # Trigger
        self.weights_trig, self.corrections_trig = zip(*[
            (w, read_file(path, form=["ptlow", "pthigh", "absetalow", "absetahigh", "corr", "unc"]))
            for w, path in self.correction_trig_paths
        ])
        self.weights_trig = np.array(self.weights_trig)
        self.corrections_trig = [
            [np.array(zip(*[sf.pop("ptlow"), sf.pop("pthigh")])),
             np.array(zip(*[sf.pop("absetalow"), sf.pop("absetahigh")])),
             np.array(sf["corr"]), np.array(sf["unc"]), np.array(sf.pop("unc"))]
            for sf in self.corrections_trig
        ]
        for sf in self.corrections_iso:
            sf[0][sf[0]==np.min(sf[0])] = 0.
            sf[0][sf[0]==np.max(sf[0])] = np.infty
            sf[1][sf[1]==np.min(sf[1])] = 0.
            sf[1][sf[1]==np.max(sf[1])] = np.infty

    def event(self, event):
        # ID
        corrs_id, corrs_id_up, corrs_id_down = get_correction_pt_abseta(
            event.MuonSelection, self.weights_id, self.corrections_id,
        )
        corrs_id_up = np.sqrt(corrs_id_up**2 + (0.01)**2)
        corrs_id_down = np.sqrt(corrs_id_down**2 + (0.01)**2)

        # ISO
        corrs_iso, corrs_iso_up, corrs_iso_down = get_correction_pt_abseta(
            event.MuonSelection, self.weights_iso, self.corrections_iso,
        )
        corrs_iso_up = np.sqrt(corrs_iso_up**2 + (0.005)**2)
        corrs_iso_down = np.sqrt(corrs_iso_down**2 + (0.005)**2)

        # Track
        corrs_track, corrs_track_up, corrs_track_down = get_correction_eta(
            event.MuonSelection, self.weights_track, self.corrections_track,
        )

        # Trig
        corrs_trig, corrs_trig_up, corrs_trig_down = get_correction_pt_abseta(
            event.MuonSelection, self.weights_trig, self.corrections_trig,
            any_pass = True,
        )
        corrs_trig_up = np.sqrt(corrs_trig_up**2 + (0.005)**2)
        corrs_trig_down = np.sqrt(corrs_trig_down**2 + (0.005)**2)

        event.Weight *= corrs_id * corrs_iso * corrs_track #* corrs_trig

def get_correction_eta(muons, weights, corrections, any_pass=False):
    etabins, corrs, corrs_up, corrs_down = [x for x in zip(*corrections)]
    return get_correction_eta_jit(
        muons.eta.content, muons.eta.starts, muons.eta.stops,
        weights, etabins, corrs, corrs_up, corrs_down, any_pass=any_pass,
    )

@njit
def get_correction_eta_jit(mueta, starts, stops, weights, inetabins,
                           incorrs, incorrs_up, incorrs_down, any_pass=False):
    nev = stops.shape[0]
    outcorrs = np.ones(nev, dtype=float32)
    outcorrs_up = np.ones(nev, dtype=float32)
    outcorrs_down = np.ones(nev, dtype=float32)

    # loop over events
    for iev, (start, stop) in enumerate(zip(starts, stops)):
        sf, sf_up2, sf_down2 = 1., 0., 0.

        # loop over muons
        for imu in range(start, stop):
            sum_weight, sum_weightcorr, sum_weightcorrup2, sum_weightcorrdown2 = 0., 0., 0., 0.

            # loop over weights
            for iw in range(weights.shape[0]):
                sum_weight += weights[iw]
                etabins = inetabins[iw]
                corr = incorrs[iw]
                corr_up = incorrs[iw]
                corr_down = incorrs[iw]

                # loop over correction bins
                for ibin in range(etabins.shape[0]):

                    # find the bin
                    if etabins[ibin,0] <= mueta[imu] < etabins[ibin,1]:
                        sum_weightcorr += weights[iw]*corr[ibin]
                        sum_weightcorrup2 += (weights[iw] * corr_up[ibin])**2
                        sum_weightcorrdown2 += (weights[iw] * corr_down[ibin])**2

                        # bin found
                        break

            # weights summed
            if any_pass:
                sf *= 1. - sum_weightcorr / sum_weight
            else:
                sf *= sum_weightcorr / sum_weight

            if sum_weightcorr > 0.:
                sf_up2 += sum_weightcorrup2 / sum_weightcorr**2
                sf_down2 += sum_weightcorrdown2 / sum_weightcorr**2

        if any_pass and start-stop>0:
            sf = 1. - sf

        # pass to output arrays
        outcorrs[iev] = sf
        outcorrs_up[iev] = np.sqrt(sf_up2)
        outcorrs_down[iev] = np.sqrt(sf_down2)

    return outcorrs, outcorrs_up, outcorrs_down

def get_correction_pt_abseta(muons, weights, corrections, any_pass=False):
    ptbins, etabins, corrs, corrs_up, corrs_down = [x for x in zip(*corrections)]
    return get_correction_pt_abseta_jit(
        muons.pt.content, muons.eta.content, muons.pt.starts, muons.pt.stops,
        weights, ptbins, etabins, corrs, corrs_up, corrs_down, any_pass=any_pass,
    )

@njit
def get_correction_pt_abseta_jit(mupt, mueta, starts, stops, weights,
                                 inptbins, inetabins,
                                 incorrs, incorrs_up, incorrs_down,
                                 any_pass=False):
    nev = stops.shape[0]
    outcorrs = np.ones(nev, dtype=float32)
    outcorrs_up = np.ones(nev, dtype=float32)
    outcorrs_down = np.ones(nev, dtype=float32)

    # loop over events
    for iev, (start, stop) in enumerate(zip(starts, stops)):
        sf, sf_up2, sf_down2 = 1., 0., 0.

        # loop over muons
        for imu in range(start, stop):
            sum_weight, sum_weightcorr, sum_weightcorrup2, sum_weightcorrdown2 = 0., 0., 0., 0.

            # loop over weights
            for iw in range(weights.shape[0]):
                sum_weight += weights[iw]
                ptbins = inptbins[iw]
                etabins = inetabins[iw]
                corr = incorrs[iw]
                corr_up = incorrs[iw]
                corr_down = incorrs[iw]

                # loop over correction bins
                for ibin in range(ptbins.shape[0]):

                    # find the bin
                    if (ptbins[ibin,0] <= mupt[imu] < ptbins[ibin,1] \
                        and etabins[ibin,0] <= abs(mueta[imu]) < etabins[ibin,1]):
                        sum_weightcorr += weights[iw]*corr[ibin]
                        sum_weightcorrup2 += (weights[iw] * corr_up[ibin])**2
                        sum_weightcorrdown2 += (weights[iw] * corr_down[ibin])**2

                        # bin found
                        break

            # weights summed
            if any_pass:
                sf *= 1. - sum_weightcorr / sum_weight
            else:
                sf *= sum_weightcorr / sum_weight

            if sum_weightcorr > 0.:
                sf_up2 += sum_weightcorrup2 / sum_weightcorr**2
                sf_down2 += sum_weightcorrdown2 / sum_weightcorr**2

        if any_pass and start-stop>0:
            sf = 1. - sf

        # pass to output arrays
        outcorrs[iev] = sf
        outcorrs_up[iev] = np.sqrt(sf_up2)
        outcorrs_down[iev] = np.sqrt(sf_down2)

    return outcorrs, outcorrs_up, outcorrs_down

def read_file(path, form):
    with open(path, 'r') as f:
        lines = [map(float, l.strip().split())
                 for l in f.read().splitlines()
                 if l.strip()[0]!="#"]
    return {k: v for k, v in zip(form, zip(*lines))}
