import numpy as np
from utils.Colours import colours_dict

inf = np.infty
pi = np.pi+0.00001

histogrammer_cfgs = [
    {
        "name": "GenPartBoson_pt_WeightNominal",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "parents": ["ZJetsToNuNu", "WJetsToLNu", "DYJetsToLL"],
        "variables": ["ev: ev.GenPartBoson_pt"],
        "bins": [[-inf]+list(np.linspace(0., 1000., 41))+[inf]],
        "weight": "ev: ev.Weight / ev.WeightEW",
    }, {
        "name": "GenPartBoson_pt_WeightEW",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "parents": ["ZJetsToNuNu", "WJetsToLNu", "DYJetsToLL"],
        "variables": ["ev: ev.GenPartBoson_pt"],
        "bins": [[-inf]+list(np.linspace(0., 1000., 41))+[inf]],
        "weight": "ev: ev.Weight",
    }, {
        "name": "METnoX_pt_WeightNominal",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.METnoX_pt"],
        "bins": [[-inf]+list(np.linspace(0., 1000., 41))+[inf]],
        "weight": "ev: ev.Weight / ev.WeightEW",
    }, {
        "name": "METnoX_pt_WeightEW",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.METnoX_pt"],
        "bins": [[-inf]+list(np.linspace(0., 1000., 41))+[inf]],
        "weight": "ev: ev.Weight",
    }, {
        "name": "DiMuon_pt_WeightNominal",
        "cutflows": ["DoubleMuon"],
        "variables": ["ev: ev.DiMuon_pt"],
        "bins": [[-inf]+list(np.linspace(0., 1000., 41))+[inf]],
        "weight": "ev: ev.Weight / ev.WeightEW",
    }, {
        "name": "DiMuon_pt_WeightEW",
        "cutflows": ["DoubleMuon"],
        "variables": ["ev: ev.DiMuon_pt"],
        "bins": [[-inf]+list(np.linspace(0., 1000., 41))+[inf]],
        "weight": "ev: ev.Weight",
    },
]

sample_colours = {
    "MET":            "black",
    "SingleMuon":     "black",
    "SingleElectron": "black",
    "ZJetsToNuNu":    colours_dict["blue"],
    "WJetsToLNu":     colours_dict["green"],
    "Diboson":        colours_dict["orange"],
    "DYJetsToLL":     colours_dict["gold"],
    "EWKV2Jets":      colours_dict["purple"],
    "SingleTop":      colours_dict["pink"],
    "TTJets":         colours_dict["violet"],
    "QCD":            colours_dict["red"],
    "G1Jet":          colours_dict["mint"],
    "VGamma":         colours_dict["yellow"],
}

axis_label = {
    "GenPartBoson_Pt": "Boson p_{T} (GeV)",
    "METnoX_pt": "E_{T}^{miss} (GeV)",
    "DiMuon_pt": "p_{T}(#mu#mu) (GeV)",
}
