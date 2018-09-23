import logging
import numpy as np

from collections import OrderedDict as odict
from utils.Lambda import Lambda

class SelectionProducer(object):
    attr_variation_conv = odict([
        ("ev.nBJetSelectionMedium",  "ev.nBJetSelectionMedium{}"),
        ("ev.MinDPhiJ1234METnoX",    "ev.MinDPhiJ1234METnoX{}"),
        ("ev.MET_pt",                "ev.MET_pt{}"),
        ("ev.MET_phi",               "ev.MET_phi{}"),
        ("ev.MET_dCaloMET",          "ev.MET_dCaloMET{}"),
        ("ev.METnoX_pt",             "ev.METnoX_pt{}"),
        ("ev.METnoX_phi",            "ev.METnoX_phi{}"),
        ("ev.Jet_pt",                "ev.Jet_pt{}"),
        ("ev.Jet_mass",              "ev.Jet_mass{}"),
        ("ev.MET.pt",                "ev.MET.pt{}"),
        ("ev.MET.phi",               "ev.MET.phi{}"),
        ("ev.MET.dCaloMET",          "ev.MET.dCaloMET{}"),
        ("ev.METnoX.pt",             "ev.METnoX.pt{}"),
        ("ev.METnoX.phi",            "ev.METnoX.phi{}"),
        ("ev.Jet.pt",                "ev.Jet.pt{}"),
        ("ev.Jet.mass",              "ev.Jet.mass{}"),
        # Collections - careful here
        ("ev.JetVeto.pt",            "ev.JetVeto.pt{}"),
        ("ev.JetVeto.mass",          "ev.JetVeto.mass{}"),
        ("ev.JetVeto",               "ev.JetVeto{}"),
        ("ev.JetSelection.pt",       "ev.JetSelection.pt{}"),
        ("ev.JetSelection.mass",     "ev.JetSelection.mass{}"),
        ("ev.JetSelection",          "ev.JetSelection{}"),
        ("ev.LeadJetSelection.pt",   "ev.LeadJetSelection.pt{}"),
        ("ev.LeadJetSelection.mass", "ev.LeadJetSelection.mass{}"),
        ("ev.LeadJetSelection",      "ev.LeadJetSelection{}"),
    ])
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.debug = False

    def begin(self, event):
        self.isdata = event.config.dataset.isdata
        es = self.event_selection

        baseline = es.data_selection if self.isdata else es.mc_selection
        self.selections = {
            "None": [],
            "Monojet": baseline + es.baseline_selection + es.monojet_selection,
            "Monojet_unblind": [(n, s)
                                for (n, s) in baseline \
                                + es.baseline_selection \
                                + es.monojet_selection
                                if n not in ["met_selection", "blind_mask", "muon_selection_fmt_0"]],
            "MonojetSB": baseline + es.baseline_selection + es.monojetsb_selection,
            "MonojetSR": baseline + es.baseline_selection + es.monojetsr_selection,
            "MonojetQCD": baseline + es.baseline_selection + es.monojetqcd_selection,
            "MonojetQCDSB": baseline + es.baseline_selection + es.monojetqcdsb_selection,
            "MonojetQCDSR": baseline + es.baseline_selection + es.monojetqcdsr_selection,
            "SingleMuon": baseline + es.baseline_selection + es.singlemuon_selection,
            "SingleMuonSB": baseline + es.baseline_selection + es.singlemuonsb_selection,
            "SingleMuonSR": baseline + es.baseline_selection + es.singlemuonsr_selection,
            "DoubleMuon": baseline + es.baseline_selection + es.doublemuon_selection,
            "DoubleMuon_unblind": [(n, s)
                                   for (n, s) in baseline \
                                   + es.baseline_selection \
                                   + es.doublemuon_selection
                                   if n not in ["met_selection", "blind_mask"]],
            "DoubleMuonSB": baseline + es.baseline_selection + es.doublemuonsb_selection,
            "DoubleMuonSR": baseline + es.baseline_selection + es.doublemuonsr_selection,
            "SingleElectron": baseline + es.baseline_selection + es.singleelectron_selection,
            "SingleElectronSB": baseline + es.baseline_selection + es.singleelectronsb_selection,
            "SingleElectronSR": baseline + es.baseline_selection + es.singleelectronsr_selection,
            "DoubleElectron": baseline + es.baseline_selection + es.doubleelectron_selection,
            "DoubleElectronSB": baseline + es.baseline_selection + es.doubleelectronsb_selection,
            "DoubleElectronSR": baseline + es.baseline_selection + es.doubleelectronsr_selection,
        }

        # Create N-1 cutflows
        additional_selections = {}
        for cutflow, selection in self.selections.items():
            for subselection in selection:
                if subselection[0] == "blind_mask":
                    continue
                new_selection = selection[:]
                new_selection.remove(subselection)
                newcutflow = "{}_remove_{}".format(cutflow, subselection[0])
                additional_selections[newcutflow] = new_selection

        # Create variation cutflows
        for cutflow, selection in self.selections.items():
            for variation in self.variations:
                new_selection = selection[:]
                for attr, new_attr in self.attr_variation_conv.items():
                    new_selection = [
                        (subselection[0],
                         subselection[1].replace(attr, new_attr.format(variation))) \
                        if attr in subselection[1] and not self.isdata \
                        else subselection
                        for subselection in new_selection
                    ]
                additional_selections[cutflow+variation] = new_selection

        self.selections.update(additional_selections)
        self.selections_lambda = {cutflow: [Lambda(cut) for name, cut in selection]
                                  for cutflow, selection in self.selections.items()}

    def event(self, event):
        if self.debug:
            logger = logging.getLogger(__name__)
            results = [cut(event) for cut in self.selections_lambda["SingleMuon"]]
            for idx in range(len(results)-1):
                results[idx+1] = results[idx+1] & results[idx]
            for idx in range(len(self.selections_lambda["SingleMuon"])):
                logger.info(str(self.selections_lambda["SingleMuon"][idx].function)+" "+str(results[idx]))

        for cutflow, selection in self.selections_lambda.items():
            if len(selection) > 0:
                cuts = reduce(lambda x, y: x & y, [cut(event) for cut in selection])
            else:
                cuts = np.ones(event.size, dtype=bool)
            setattr(event, "Cutflow_{}".format(cutflow), cuts)

    def end(self):
        self.selections_lambda = {}
