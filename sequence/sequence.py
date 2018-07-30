import Modules

collection_creator = Modules.CollectionCreator(
    name = "collection_creator",
    collections = ["CaloMET", "MET", "Jet", "Electron", "Muon", "Photon",
                   "Tau", "GenMET", "GenPart", "GenJet", "GenDressedLepton"],
)

skim_collections = Modules.SkimCollections(
    name = "skim_collections",
    selection_dict = {
        ("Jet", "JetVeto"): "j: (j.pt>40.) & "\
                               "(j.jetId>=1) & "\
                               "((j.puId>=1) | (j.pt>50.))",
        ("Jet", "JetSelection"): "j: (j.pt>40.) & "\
                                    "(np.abs(j.eta)<2.4) & "\
                                    "(j.jetId>=1) & "\
                                    "((j.puId>=1) | (j.pt>50.))",
        ("Muon", "MuonVeto"): "u: (u.pt>10.) & "\
                                 "(np.abs(u.eta)<2.5) & "\
                                 "(np.abs(u.pfRelIso04_all)<0.15) & "\
                                 "(np.abs(u.dxy)<0.5) & "\
                                 "(np.abs(u.dz)<1.0)",
        ("Muon", "MuonSelection"): "u: (u.pt>30.) &"\
                                      "(np.abs(u.eta)<2.1) & "\
                                      "(np.abs(u.pfRelIso04_all)<0.15) &"\
                                      "(u.tightId>=1)",
        ("Electron", "ElectronVeto"): "e: (e.pt>10.) & "\
                                         "(np.abs(e.eta)<2.5) & "\
                                         "(e.cutBased>=1) & "\
                                         "(np.abs(e.dxy)<0.118) & "\
                                         "(np.abs(e.dz)<0.822) & "\
                                         "(e.convVeto)",
        ("Electron", "ElectronSelection"): "e: (e.pt>30.) & "\
                                              "(np.abs(e.eta)<2.1) & "\
                                              "(e.cutBased>=4) & "\
                                              "(((np.abs(e.eta)<=1.479) & "\
                                                "(np.abs(e.dxy)<0.05) & "\
                                                "(np.abs(e.dz)<0.1)) | "\
                                               "((np.abs(e.eta)>1.479) & "\
                                                "(np.abs(e.dxy)<0.1) & "\
                                                "(np.abs(e.dz)<0.2))) & "\
                                              "(e.convVeto)",
        ("Photon", "PhotonVeto"): "y: (y.pt>25.) & "\
                                     "(np.abs(y.eta)<2.5) & "\
                                     "(y.cutBased>=1) & "\
                                     "(~y.pixelSeed)",
        ("Photon", "PhotonSelection"): "y: (y.pt>165.) & "\
                                          "(np.abs(y.eta)<1.45) & "\
                                          "(y.cutBased>=3) & "\
                                          "(~y.pixelSeed)",
        ("Tau", "TauVeto"): "t: (t.pt>20.) & "\
                               "(np.abs(t.eta)<2.3) & "\
                               "(t.idMVAoldDM>=1)",
        ("Tau", "TauSelection"): "t: (t.pt>40.) & "\
                               "(np.abs(t.eta)<2.1) & "\
                               "(t.idMVAoldDM>=8)",
    }
)

jet_cross_cleaning = Modules.ObjectCrossCleaning(
    name = "jet_cross_cleaning",
    clean_collections = ("JetVeto", "JetSelection"),
    ref_collections = ("MuonVeto", "ElectronVeto", "PhotonVeto"),
)

tau_cross_cleaning = Modules.ObjectCrossCleaning(
    name = "tau_cross_cleaning",
    clean_collections = ("TauVeto", "TauSelection"),
    ref_collections = ("MuonVeto", "ElectronVeto"),
)

jec_variations = Modules.JecVariations(
    jes_unc_file = "/vols/build/cms/sdb15/atuproot/data/jecs/Summer16_23Sep2016V4_MC_Uncertainty_AK4PFchs.txt",
    variation = None,
)

sequence = [
    collection_creator,
    jec_variations,
    skim_collections,
    jet_cross_cleaning,
    tau_cross_cleaning,
]
