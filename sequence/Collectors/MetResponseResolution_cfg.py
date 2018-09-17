import numpy as np
from utils.Colours import colours_dict

inf = np.infty

dimuon_categories = [("MET", "DoubleMuon_unblind"), ("SingleMuon", "DoubleMuon_unblind")]

bins = [200., 207., 214., 220., 226., 232., 238., 244., 250., 258., 268., 279.,
        292., 307., 326., 349., 380., 431., 563., 695.]

histogrammer_cfgs = [
    {
        "name": ["METnoX_diMuonParaProjPt_Minus_DiMuon_pt",
                 "DiMuon_pt"],
        "categories": dimuon_categories,
        "variables": ["ev: ev.METnoX_diMuonParaProjPt_Minus_DiMuon_pt",
                      "ev: ev.DiMuon_pt"],
        "bins": [[-inf]+list(np.linspace(-250, 250., 51))+[inf],
                 [-inf]+bins+[inf]],
        "weights": [("nominal", "ev: ev.Weight_{dataset}")],
    }, {
        "name": ["METnoX_diMuonPerpProjPt",
                 "DiMuon_pt"],
        "categories": dimuon_categories,
        "variables": ["ev: ev.METnoX_diMuonPerpProjPt",
                      "ev: ev.DiMuon_pt"],
        "bins": [[-inf]+list(np.linspace(-250., 250., 51))+[inf],
                 [-inf]+bins+[inf]],
        "weights": [("nominal", "ev: ev.Weight_{dataset}")],
    }, {
        "name": ["METnoX_diMuonParaProjPt_Div_DiMuon_pt",
                 "DiMuon_pt"],
        "categories": dimuon_categories,
        "variables": ["ev: ev.METnoX_diMuonParaProjPt_Div_DiMuon_pt",
                      "ev: ev.DiMuon_pt"],
        "bins": [[-inf]+list(np.linspace(0., 2., 51))+[inf],
                 [-inf]+bins+[inf]],
        "weights": [("nominal", "ev: ev.Weight_{dataset}")],
    }, {
        "name": ["METnoX_diMuonPerpProjPt_Plus_DiMuon_pt_Div_DiMuon_pt",
                 "DiMuon_pt"],
        "categories": dimuon_categories,
        "variables": ["ev: ev.METnoX_diMuonPerpProjPt_Plus_DiMuon_pt_Div_DiMuon_pt",
                      "ev: ev.DiMuon_pt"],
        "bins": [[-inf]+list(np.linspace(0., 2., 51))+[inf],
                 [-inf]+bins+[inf]],
        "weights": [("nominal", "ev: ev.Weight_{dataset}")],
    }, {
        "name": ["METnoX_diMuonParaProjPt_Minus_DiMuon_pt",
                 "METnoX_pt"],
        "categories": dimuon_categories,
        "variables": ["ev: ev.METnoX_diMuonParaProjPt_Minus_DiMuon_pt",
                      "ev: ev.METnoX_pt"],
        "bins": [[-inf]+list(np.linspace(-250, 250., 51))+[inf],
                 [-inf]+bins+[inf]],
        "weights": [("nominal", "ev: ev.Weight_{dataset}")],
    }, {
        "name": ["METnoX_diMuonPerpProjPt",
                 "METnoX_pt"],
        "categories": dimuon_categories,
        "variables": ["ev: ev.METnoX_diMuonPerpProjPt",
                      "ev: ev.METnoX_pt"],
        "bins": [[-inf]+list(np.linspace(-250., 250., 51))+[inf],
                 [-inf]+bins+[inf]],
        "weights": [("nominal", "ev: ev.Weight_{dataset}")],
    }, {
        "name": ["METnoX_diMuonParaProjPt_Div_DiMuon_pt",
                 "METnoX_pt"],
        "categories": dimuon_categories,
        "variables": ["ev: ev.METnoX_diMuonParaProjPt_Div_DiMuon_pt",
                      "ev: ev.METnoX_pt"],
        "bins": [[-inf]+list(np.linspace(0., 2., 51))+[inf],
                 [-inf]+bins+[inf]],
        "weights": [("nominal", "ev: ev.Weight_{dataset}")],
    }, {
        "name": ["METnoX_diMuonPerpProjPt_Plus_DiMuon_pt_Div_DiMuon_pt",
                 "METnoX_pt"],
        "categories": dimuon_categories,
        "variables": ["ev: ev.METnoX_diMuonPerpProjPt_Plus_DiMuon_pt_Div_DiMuon_pt",
                      "ev: ev.METnoX_pt"],
        "bins": [[-inf]+list(np.linspace(0., 2., 51))+[inf],
                 [-inf]+bins+[inf]],
        "weights": [("nominal", "ev: ev.Weight_{dataset}")],
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
    "DiMuon_pt": r'$p_{T}(\mu\mu)$ (GeV)',
    "METnoX_pt": r'$E_{T}^{miss}$ (GeV)',
    "METnoX_diMuonParaProjPt_Minus_DiMuon_pt": r'$E_{T,\parallel}^{miss} - p_{T}(\mu\mu)$ (GeV)',
    "METnoX_diMuonPerpProjPt": r'$E_{T,\perp}^{miss}$ (GeV)',
    "METnoX_diMuonParaProjPt_Div_DiMuon_pt": r'$E_{T,\parallel}^{miss} / p_{T}(\mu\mu)$',
    "METnoX_diMuonPerpProjPt_Plus_DiMuon_pt_Div_DiMuon_pt": r'$(E_{T,\perp}^{miss}+p_{T}(\mu\mu)) / p_{T}(\mu\mu)$',
}
