import numpy as np
from utils.Colours import colours_dict

inf = np.infty
pi = np.pi+0.00001

# dataset-cutflows split into regions
monojet_categories = [("MET", "Monojet"), ("MET", "MonojetSB"), ("MET", "MonojetSR"),
                      ("MET", "MonojetQCD"), ("MET", "MonojetQCDSB"), ("MET", "MonojetQCDSR")]

muon_categories = [("MET", "SingleMuon"), ("MET", "SingleMuonSB"), ("MET", "SingleMuonSR"),
                   ("SingleMuon", "SingleMuon"), ("SingleMuon", "SingleMuonSB"), ("SingleMuon", "SingleMuonSR")]
dimuon_categories = [("MET", "DoubleMuon"), ("MET", "DoubleMuonSB"), ("MET", "DoubleMuonSR"),
                     ("SingleMuon", "DoubleMuon"),("SingleMuon", "DoubleMuonSB"), ("SingleMuon", "DoubleMuonSR")]

ele_categories = [("MET", "SingleElectron"), ("MET", "SingleElectronSB"), ("MET", "SingleElectronSR")]
diele_categories = [("MET", "DoubleElectron"), ("MET", "DoubleElectronSB"), ("MET", "DoubleElectronSR")]

categories = monojet_categories + muon_categories + dimuon_categories + \
                                  ele_categories + diele_categories

histogrammer_cfgs = [
    {
        "name": "METnoX_pt",
        "categories": categories,
        "variables": ["ev: ev.METnoX_pt"],
        "bins": [[-inf]+list(np.linspace(0., 1000., 41))+[inf]],
        "weights": [
            ("nominal",       "ev: ev.Weight_{dataset}"),
            ("pileupUp",      "ev: ev.Weight_{dataset}*ev.Weight_pileupUp"),
            ("pileupDown",    "ev: ev.Weight_{dataset}*ev.Weight_pileupDown"),
            ("metTrigSFUp",   "ev: ev.Weight_{dataset}*ev.Weight_metTrigSFUp"),
            ("metTrigSFDown", "ev: ev.Weight_{dataset}*ev.Weight_metTrigSFDown"),
            ("muonIdUp",      "ev: ev.Weight_{dataset}*ev.Weight_muonIdUp"),
            ("muonIdDown",    "ev: ev.Weight_{dataset}*ev.Weight_muonIdDown"),
            ("muonIsoUp",     "ev: ev.Weight_{dataset}*ev.Weight_muonIsoUp"),
            ("muonIsoDown",   "ev: ev.Weight_{dataset}*ev.Weight_muonIsoDown"),
            ("muonTrackUp",   "ev: ev.Weight_{dataset}*ev.Weight_muonTrackUp"),
            ("muonTrackDown", "ev: ev.Weight_{dataset}*ev.Weight_muonTrackDown"),
            ("muonTrigUp",    "ev: ev.Weight_{dataset}*ev.Weight_muonTrigUp"),
            ("muonTrigDown",  "ev: ev.Weight_{dataset}*ev.Weight_muonTrigDown"),
        ],
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
    "Weight": r'Weight',
    "METnoX_pt": r'$E_{T}^{miss}$ (GeV)',
    "METnoX_phi": r'$E_{T}^{miss}\ \phi$',
    "METnoX_diMuonParaProjPt_Minus_DiMuon_pt": r'$E_{T,\parallel}^{miss} - p_{T}(\mu\mu)$ (GeV)',
    "METnoX_diMuonPerpProjPt": r'$E_{T,\perp}^{miss}$ (GeV)',
    "DiMuon_pt": r'$p_{T}(\mu\mu)$ (GeV)',
    "DiMuon_phi": r'$p_{T}(\mu\mu)\ \phi',
    "MET_pt": r'$E_{T,PF}^{miss}$ (GeV)',
    "MET_phi": r'$E_{T,PF}^{miss}\ \phi$',
    "CaloMET_pt": r'$E_{T,Calo.}^{miss}$ (GeV)',
    "CaloMET_phi": r'$E_{T,Calo.}^{miss}\ \phi$',
    "HT40": r'$H_{T}(p_{T,j} > 40)$ (GeV)',
    "MHT40_pt": r'$H_{T}^{miss}(p_{T,j} > 40)$ (GeV)',
    "MHT40_phi": r'$H_{T}^{miss}(p_{T,j} > 40)\ \phi$',
    "MHT40_pt_div_METnoX_pt": r'$H_{T}^{miss}(p_{T,j} > 40) / E_{T}^{miss}$',
    "MinDPhiJ1234METnoX": r'$min( \Delta\Phi(j_{1,2,3,4}, E_{T}^{miss}) )$',
    "MET_dCaloMET": r'$|E_{T,PF}^{miss} - E_{T,Calo.}^{miss}| / E_{T}^{miss}$',
    "MTW": r'$m_{T}(l, E_{T,PF}^{miss})$ (GeV)',
    "MLL": r'$m(l, l)$ (GeV)',
    "MLL_wide": r'$m(l, l)$ (GeV)',
    "nJetVeto": r'No. clean veto jets',
    "nJetSelection": r'No. clean selected jets',
    "LeadJetSelection_pt": r'$p_{T}(j_{0})$ (GeV)',
    "LeadJetSelection_eta": r'$\eta(j_{0})$',
    "LeadJetSelection_phi": r'$\phi(j_{0})$',
    "LeadJetSelection_chEmEF": r'$f_{\mathrm{Ch. EM En.}}(j_{0})$',
    "LeadJetSelection_chHEF": r'$f_{\mathrm{Ch. Had. En.}}(j_{0})$',
    "LeadJetSelection_neEmEF": r'$f_{\mathrm{Neut. EM En.}}(j_{0})$',
    "LeadJetSelection_neHEF": r'$f_{\mathrm{Neut. Had. En.}}(j_{0})$',
    "nMuonVeto": r'No. veto muon',
    "nMuonSelection": r'No. selected muon',
    "nElectronVeto": r'No. veto electron',
    "nElectronSelection": r'No. selected electron',
    "nPhotonVeto": r'No. veto photon',
    "nPhotonSelection": r'No. selected photon',
    "nTauVeto": r'No. clean selected $\tau$',
    "nTauSelection": r'No. clean selected $\tau$',
    "nBJetSelectionMedium": r'No. clean selected b-jets (medium WP)',
    "LeadMuonSelection_pt": r'$p_{T}(\mu_{0})$ (GeV)',
    "LeadMuonSelection_eta": r'$\eta(\mu_{0})$',
    "LeadMuonSelection_phi": r'$\phi(\mu_{0})$',
    "SecondMuonSelection_pt": r'$p_{T}(\mu_{1})$ (GeV)',
    "SecondMuonSelection_eta": r'$\eta(\mu_{1})$',
    "SecondMuonSelection_phi": r'$\phi(\mu_{1})$',
    "LeadElectronSelection_pt": r'$p_{T}(e_{0})$ (GeV)',
    "LeadElectronSelection_eta": r'$\eta(e_{0})$',
    "LeadElectronSelection_phi": r'$\phi(e_{0})$',
    "SecondElectronSelection_pt": r'$p_{T}(e_{1})$ (GeV)',
    "SecondElectronSelection_eta": r'$\eta(e_{1})$',
    "SecondElectronSelection_phi": r'$\phi(e_{1})$',
    "PV_npvsGood": r'No. of good PVs',
    "LeptonDevay": r'Lepton decay pdg ID',
    "nGenBosons": r'No. of gen. bosons',
    "GenPartBoson_pt": r'Gen. $p_{T}(V)$ (GeV)',
    "GenPartBoson_eta": r'Gen. $\eta(V)$ (GeV)',
    "GenPartBoson_phi": r'Gen. $\phi(V)$ (GeV)',
    "GenPartBoson_mass": r'Gen. $m(V)$ (GeV)',
}
