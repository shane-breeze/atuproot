from utils.classes import EmptyClass
physics_object_selection = EmptyClass()

jet_veto = "j: (j.pt>40.) & "\
              "(j.jetId>=1) & "\
              "((j.puId>=1) | (j.pt>50.))"
jet_sele = "j: (j.pt>40.) & "\
              "(np.abs(j.eta)<2.4) & "\
              "(j.jetId>=1) & "\
              "((j.puId>=1) | (j.pt>50.))"

muo_veto = "u: (u.pt>10.) & "\
              "(np.abs(u.eta)<2.5) & "\
              "(np.abs(u.pfRelIso04_all)<0.25) & "\
              "(np.abs(u.dxy)<0.5) & "\
              "(np.abs(u.dz)<1.0)"
muo_sele = "u: (u.pt>30.) &"\
              "(np.abs(u.eta)<2.1) & "\
              "(np.abs(u.pfRelIso04_all)<0.15) &"\
              "(u.tightId>=1)"

ele_veto = "e: (e.pt>10.) & "\
              "(np.abs(e.eta)<2.5) & "\
              "(e.cutBased>=1) & "\
              "(np.abs(e.dxy)<0.118) & "\
              "(np.abs(e.dz)<0.822) & "\
              "(e.convVeto)"
ele_sele = "e: (e.pt>20.) & "\
              "(np.abs(e.eta)<2.5) & "\
              "(e.cutBased>=4) & "\
              "(((np.abs(e.eta)<=1.479) & "\
                "(np.abs(e.dxy)<0.05) & "\
                "(np.abs(e.dz)<0.1)) | "\
               "((np.abs(e.eta)>1.479) & "\
                "(np.abs(e.dxy)<0.1) & "\
                "(np.abs(e.dz)<0.2))) & "\
              "(e.convVeto)"

pho_veto = "y: (y.pt>25.) & "\
              "(np.abs(y.eta)<2.5) & "\
              "(y.cutBased>=1) & "\
              "(~y.pixelSeed)"
pho_sele = "y: (y.pt>165.) & "\
              "(np.abs(y.eta)<1.45) & "\
              "(y.cutBased>=3) & "\
              "(~y.pixelSeed)"

tau_veto = "t: (t.pt>20.) & "\
              "(np.abs(t.eta)<2.3) & "\
              "(t.idMVAoldDM>=1)"
tau_sele = "t: (t.pt>40.) & "\
              "(np.abs(t.eta)<2.1) & "\
              "(t.idMVAoldDM>=8)"

physics_object_selection.selection_dict = {
    ("Jet",      "JetVeto"):           jet_veto,
    ("Jet",      "JetSelection"):      jet_sele,
    ("Muon",     "MuonVeto"):          muo_veto,
    ("Muon",     "MuonSelection"):     muo_sele,
    ("Electron", "ElectronVeto"):      ele_veto,
    ("Electron", "ElectronSelection"): ele_sele,
    ("Photon",   "PhotonVeto"):        pho_veto,
    ("Photon",   "PhotonSelection"):   pho_sele,
    ("Tau",      "TauVeto"):           tau_veto,
    ("Tau",      "TauSelection"):      tau_sele,
}
