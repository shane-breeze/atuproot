import re

trigger_selection = {
    "MET": {
        "B1": ['HLT_PFMETNoMu90_PFMHTNoMu90_IDTight',
               'HLT_PFMETNoMu100_PFMHTNoMu100_IDTight',
               'HLT_PFMETNoMu110_PFMHTNoMu110_IDTight',
               'HLT_PFMETNoMu120_PFMHTNoMu120_IDTight',
               'HLT_PFMET170_NotCleaned',
               'HLT_PFMET170_BeamHaloCleaned',
               'HLT_PFMET170_HBHECleaned',
               'HLT_PFMET170_HBHE_BeamHaloCleaned'],
        "B2": ['HLT_PFMETNoMu100_PFMHTNoMu100_IDTight',
               'HLT_PFMETNoMu110_PFMHTNoMu110_IDTight',
               'HLT_PFMETNoMu120_PFMHTNoMu120_IDTight',
               'HLT_PFMET170_NotCleaned',
               'HLT_PFMET170_BeamHaloCleaned',
               'HLT_PFMET170_HBHECleaned',
               'HLT_PFMET170_HBHE_BeamHaloCleaned'],
        "C1": ['HLT_PFMETNoMu100_PFMHTNoMu100_IDTight',
               'HLT_PFMETNoMu110_PFMHTNoMu110_IDTight',
               'HLT_PFMETNoMu120_PFMHTNoMu120_IDTight',
               'HLT_PFMET170_HBHECleaned',
               'HLT_PFMET170_HBHE_BeamHaloCleaned'],
        "D1": ['HLT_PFMETNoMu110_PFMHTNoMu110_IDTight',
               'HLT_PFMETNoMu120_PFMHTNoMu120_IDTight',
               'HLT_PFMET170_HBHECleaned',
               'HLT_PFMET170_HBHE_BeamHaloCleaned'],
        "E1": ['HLT_PFMETNoMu110_PFMHTNoMu110_IDTight',
               'HLT_PFMETNoMu120_PFMHTNoMu120_IDTight',
               'HLT_PFMET170_HBHECleaned',
               'HLT_PFMET170_HBHE_BeamHaloCleaned'],
        "F1": ['HLT_PFMETNoMu110_PFMHTNoMu110_IDTight',
               'HLT_PFMETNoMu120_PFMHTNoMu120_IDTight',
               'HLT_PFMET170_HBHECleaned',
               'HLT_PFMET170_HBHE_BeamHaloCleaned'],
        "G1": ['HLT_PFMETNoMu110_PFMHTNoMu110_IDTight',
               'HLT_PFMETNoMu120_PFMHTNoMu120_IDTight',
               'HLT_PFMET170_HBHECleaned',
               'HLT_PFMET170_HBHE_BeamHaloCleaned'],
        "H2": ['HLT_PFMETNoMu120_PFMHTNoMu120_IDTight',
               'HLT_PFMET170_HBHECleaned',
               'HLT_PFMET170_HBHE_BeamHaloCleaned'],
        "H3": ['HLT_PFMETNoMu110_PFMHTNoMu110_IDTight',
               'HLT_PFMETNoMu120_PFMHTNoMu120_IDTight',
               'HLT_PFMET170_HBHECleaned',
               'HLT_PFMET170_HBHE_BeamHaloCleaned'],
    },
    "SingleMuon": ["HLT_IsoMu24", "HLT_IsoTkMu24"],
    "SingleElectron": ["HLT_Ele27_WPTight_Gsf"],
}

class TriggerChecker(object):
    regex = re.compile("^(?P<dataset>[a-zA-Z0-9]*)_Run2016(?P<run_letter>[a-zA-Z])_v(?P<version>[0-9])$")
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def begin(self, event):
        match = self.regex.search(event.config.dataset.name)
        if match:
            dataset = match.group("dataset")
            run = match.group("run_letter")+match.group("version")

        self.trigger_list = trigger_selection[dataset]
        if dataset == "MET":
            self.trigger_list = self.trigger_list[run]

    def event(self, event):
        event.IsTriggered = reduce(lambda x,y: x | y,
                                   [getattr(event, trigger)
                                    for trigger in self.trigger_list
                                    if event.hasbranch(trigger)])
