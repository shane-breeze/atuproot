import numpy as np
from utils.Colours import colours_dict

inf = np.infty
pi = np.pi+0.00001

histogrammer_cfgs = [
    {
        "name": "Weight",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.Weight"],
        "bins": [[-inf]+list(np.linspace(0., 100., 101))+[inf]],
    }, {
        "name": "METnoX_pt",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.METnoX_pt"],
        "bins": [[-inf]+list(np.linspace(0., 1600., 65))+[inf]],
    }, {
        "name": "MET_pt",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.MET_pt"],
        "bins": [[-inf]+list(np.linspace(0., 1600., 65))+[inf]],
    }, {
        "name": "CaloMET_pt",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.CaloMET_pt"],
        "bins": [[-inf]+list(np.linspace(0., 1600., 65))+[inf]],
    }, {
        "name": "HT40",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.HT40"],
        "bins": [[-inf]+list(np.linspace(0., 5000., 101))+[inf]],
    }, {
        "name": "MHT40_pt",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.MHT40_pt"],
        "bins": [[-inf]+list(np.linspace(0., 1600., 65))+[inf]],
    }, {
        "name": "MHT40_pt_div_METnoX_pt",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.MHT40_pt / ev.METnoX_pt"],
        "bins": [[-inf]+list(np.linspace(0., 3., 61))+[inf]],
    }, {
        "name": "MinDPhiJ1234METnoX",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.MinDPhiJ1234METnoX"],
        "bins": [[-inf]+list(np.linspace(0., 1.02*pi, 103))+[inf]],
    }, {
        "name": "MET_dCaloMET",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.MET_dCaloMET"],
        "bins": [[-inf]+list(np.linspace(0., 2., 201))+[inf]],
    }, {
        "name": "nJetSelection",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.JetSelection.size"],
        "bins": [[-inf]+list(np.linspace(0., 10., 11))+[inf]],
    }, {
        "name": "LeadJetSelection_pt",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.LeadJetSelection_pt"],
        "bins": [[-inf]+list(np.linspace(0., 2000., 201))+[inf]],
    }, {
        "name": "LeadJetSelection_eta",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.LeadJetSelection_eta"],
        "bins": [[-inf]+list(np.linspace(-5., 5., 101))+[inf]],
    }, {
        "name": "LeadJetSelection_chHEF",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.LeadJetSelection_chHEF"],
        "bins": [[-inf]+list(np.linspace(0., 1., 101))+[inf]],
    }, {
        "name": "nMuonSelection",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.MuonSelection.size"],
        "bins": [[-inf]+list(np.linspace(0., 5., 6))+[inf]],
    }, {
        "name": "nElectronSelection",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.ElectronSelection.size"],
        "bins": [[-inf]+list(np.linspace(0., 5., 6))+[inf]],
    }, {
        "name": "nPhotonSelection",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.PhotonSelection.size"],
        "bins": [[-inf]+list(np.linspace(0., 5., 6))+[inf]],
    }, {
        "name": "nTauSelection",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.TauSelection.size"],
        "bins": [[-inf]+list(np.linspace(0., 5., 6))+[inf]],
    }, {
        "name": "nBJetSelectionMedium",
        "cutflows": ["Monojet", "SingleMuon", "DoubleMuon", "SingleElectron", "DoubleElectron", "MonojetQCD"],
        "variables": ["ev: ev.nBJetSelectionMedium"],
        "bins": [[-inf]+list(np.linspace(0., 5., 6))+[inf]],
    }, {
        "name": "LeadMuonSelection_pt",
        "cutflows": ["SingleMuon", "DoubleMuon"],
        "variables": ["ev: ev.LeadMuonSelection_pt"],
        "bins": [[-inf]+list(np.linspace(0., 1000., 101))+[inf]],
    }, {
        "name": "LeadMuonSelection_eta",
        "cutflows": ["SingleMuon", "DoubleMuon"],
        "variables": ["ev: ev.LeadMuonSelection_eta"],
        "bins": [[-inf]+list(np.linspace(-5., 5., 101))+[inf]],
    }, {
        "name": "LeadElectronSelection_pt",
        "cutflows": ["SingleElectron", "DoubleElectron"],
        "variables": ["ev: ev.LeadElectronSelection_pt"],
        "bins": [[-inf]+list(np.linspace(0., 1000., 101))+[inf]],
    }, {
        "name": "LeadElectronSelection_eta",
        "cutflows": ["SingleElectron", "DoubleElectron"],
        "variables": ["ev: ev.LeadElectronSelection_eta"],
        "bins": [[-inf]+list(np.linspace(-5., 5., 101))+[inf]],
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
    "Weight": "Weight",
    "METnoX_pt": "E_{T}^{miss} (GeV)",
    "MET_pt": "E_{T,PF}^{miss} (GeV)",
    "CaloMET_pt": "E_{T,Calo.}^{miss} (GeV)",
    "HT40": "H_{T}(p_{T,j} > 40) (GeV)",
    "MHT40_pt": "H_{T}^{miss}(p_{T,j} > 40) (GeV)",
    "MHT40_pt_div_METnoX_pt": "H_{T}^{miss}(p_{T,j} > 40) / E_{T}^{miss}",
    "MinDPhiJ1234METnoX": "min( #Delta#Phi(j_{1,2,3,4}, E_{T}^{miss}) )",
    "MET_dCaloMET": "|E_{T,PF}^{miss} - E_{T,Calo.}^{miss}| / E_{T}^{miss}",
    "nJetSelection": "Number of clean selected jets",
    "LeadJetSelection_pt": "p_{T}(j_0) (GeV)",
    "LeadJetSelection_eta": "#eta(j_0) (GeV)",
    "LeadJetSelection_chHEF": "f_{Ch. Had. En.}(j_0)",
    "nMuonSelection": "Number of selected muons",
    "nElectronSelection": "Number of selected electrons",
    "nPhotonSelection": "Number of selected photons",
    "nTauSelection": "Number of clean selected #tau",
    "nBJetSelectionMedium": "Number of clean selected jets passing medium b-jet WP",
    "LeadMuonSelection_pt": "p_{T}(#mu_0) (GeV)",
    "LeadMuonSelection_eta": "#eta(#mu_0) (GeV)",
    "LeadElectronSelection_pt": "p_{T}(e_0) (GeV)",
    "LeadElectronSelection_eta": "#eta(e_0) (GeV)",
}
