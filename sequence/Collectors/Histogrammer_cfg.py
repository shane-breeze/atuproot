import numpy as np

histogrammer_cfgs = [
    {
        "name": "METnoX_pt",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["METnoX_pt"],
        "bins": [[-np.infty]+list(np.linspace(0., 2000., 201))+[np.infty]],
    },
]
