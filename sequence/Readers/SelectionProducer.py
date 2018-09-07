import logging
import numpy as np

import sequence.event_selection as es
from utils.Lambda import Lambda

class SelectionProducer(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.debug = False

    def begin(self, event):
        self.isdata = event.config.dataset.isdata

        baseline = es.data_selection if self.isdata else es.mc_selection
        self.selections = {
            "Monojet": baseline + es.baseline_selection + es.monojet_selection,
            "MonojetSB": baseline + es.baseline_selection + es.monojetsb_selection,
            "MonojetSR": baseline + es.baseline_selection + es.monojetsr_selection,
            "MonojetQCD": baseline + es.baseline_selection + es.monojetqcd_selection,
            "MonojetQCDSB": baseline + es.baseline_selection + es.monojetqcdsb_selection,
            "MonojetQCDSR": baseline + es.baseline_selection + es.monojetqcdsr_selection,
            "SingleMuon": baseline + es.baseline_selection + es.singlemuon_selection,
            "SingleMuonSB": baseline + es.baseline_selection + es.singlemuonsb_selection,
            "SingleMuonSR": baseline + es.baseline_selection + es.singlemuonsr_selection,
            "DoubleMuon": baseline + es.baseline_selection + es.doublemuon_selection,
            "DoubleMuon_unblind": baseline + es.baseline_selection + es.doublemuon_selection[1:],
            "DoubleMuonSB": baseline + es.baseline_selection + es.doublemuonsb_selection,
            "DoubleMuonSR": baseline + es.baseline_selection + es.doublemuonsr_selection,
            "SingleElectron": baseline + es.baseline_selection + es.singleelectron_selection,
            "SingleElectronSB": baseline + es.baseline_selection + es.singleelectronsb_selection,
            "SingleElectronSR": baseline + es.baseline_selection + es.singleelectronsr_selection,
            "DoubleElectron": baseline + es.baseline_selection + es.doubleelectron_selection,
            "DoubleElectronSB": baseline + es.baseline_selection + es.doubleelectronsb_selection,
            "DoubleElectronSR": baseline + es.baseline_selection + es.doubleelectronsr_selection,
        }

        self.selections_lambda = {cutflow: [Lambda(cut) for cut in selection]
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
            setattr(event, "Cutflow_{}".format(cutflow),
                    reduce(lambda x, y: x & y, [cut(event) for cut in selection]))

    def end(self):
        self.selections_lambda = {}
