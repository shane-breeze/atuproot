import numpy as np
from utils.Colours import colours_dict
inf = np.infty

histogrammer_cfgs = [
    {
        "name": "GenPartBoson_pt",
        "categories": [("MET", "Monojet")],
        "variables": ["ev: ev.GenPartBoson_pt"],
        "bins": [[-inf]+list(np.linspace(0., 2000., 51))+[inf]],
        "weight": "ev: ev.Weight_XsLumi",
    }, {
        "name": "GenPartBoson_pt_corrected",
        "categories": [("MET", "Monojet")],
        "variables": ["ev: ev.GenPartBoson_pt"],
        "bins": [[-inf]+list(np.linspace(0., 2000., 51))+[inf]],
        "weight": "ev: ev.Weight_XsLumi*ev.WeightQCDEWK",
    },
]

sample_colours = {
    "MET":            "black",
    "SingleMuon":     "black",
    "SingleElectron": "black",
    "ZJetsToNuNu":    colours_dict["blue"],
    "WJetsToLNu":     colours_dict["green"],
    "WJetsToENu":     colours_dict["lgreen"],
    "WJetsToMuNu":    colours_dict["green"],
    "WJetsToTauNu":   colours_dict["teal"],
    "Diboson":        colours_dict["orange"],
    "DYJetsToLL":     colours_dict["gold"],
    "DYJetsToEE":     colours_dict["gold1"],
    "DYJetsToMuMu":   colours_dict["gold2"],
    "DYJetsToTauTau": colours_dict["gold3"],
    "EWKV2Jets":      colours_dict["purple"],
    "SingleTop":      colours_dict["pink"],
    "TTJets":         colours_dict["violet"],
    "QCD":            colours_dict["red"],
    "G1Jet":          colours_dict["mint"],
    "VGamma":         colours_dict["yellow"],
    "Minor":          colours_dict["gray"],
}

sample_names = {
    "MET":            r'MET',
    "SingleMuon":     r'Single Muon',
    "SingleElectron": r'Single Electron',
    "ZJetsToNuNu":    r'$Z_{\nu\nu}$+jets',
    "WJetsToLNu":     r'$W_{l\nu}$+jets',
    "WJetsToENu":     r'$W_{e\nu}$+jets',
    "WJetsToMuNu":    r'$W_{\mu\nu}$+jets',
    "WJetsToTauNu":   r'$W_{\tau\nu}$+jets',
    "Diboson":        r'Diboson',
    "DYJetsToLL":     r'$Z/\gamma^{*}_{ll}$+jets',
    "DYJetsToEE":     r'$Z/\gamma^{*}_{ee}$+jets',
    "DYJetsToMuMu":   r'$Z/\gamma^{*}_{\mu\mu}$+jets',
    "DYJetsToTauTau": r'$Z/\gamma^{*}_{\tau\tau}$+jets',
    "EWKV2Jets":      r'VBS',
    "SingleTop":      r'Single Top',
    "TTJets":         r'$t\bar{t}$+jets',
    "QCD":            r'Multijet',
    "G1Jet":          r'$\gamma$+jets',
    "VGamma":         r'$V+\gamma$',
    "Minor":          r'Minors',
}

axis_label = {
    "GenPartBoson_pt": r'$p_{T}(V)$ (GeV)',
    "GenPartBoson_pt_corrected": r'Corrected $p_{T}(V)$ (GeV)',
}
