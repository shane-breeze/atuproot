import Modules
from physics_object_selection import selection_dict

collection_creator = Modules.CollectionCreator(
    name = "collection_creator",
    collections = ["CaloMET", "MET", "Jet", "Electron", "Muon", "Photon",
                   "Tau", "GenMET", "GenPart", "GenJet", "GenDressedLepton"],
)

skim_collections = Modules.SkimCollections(
    name = "skim_collections",
    selection_dict = selection_dict,
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

event_sums_producer = Modules.EventSumsProducer()
inv_mass_producer = Modules.InvMassProducer()
gen_boson_producer = Modules.GenBosonProducer()

weight_creator = Modules.WeightCreator()
weight_xsection_lumi = Modules.WeightXsLumi()
weight_pu = Modules.WeightPileup(
    correction_file = "/vols/build/cms/sdb15/atuproot/data/pileup/nTrueInt_corrections.txt",
    overflow = True,
)

sequence = [
    collection_creator,
    jec_variations,
    skim_collections,
    jet_cross_cleaning,
    tau_cross_cleaning,
    event_sums_producer,
    inv_mass_producer,
    gen_boson_producer,
    weight_creator,
    weight_xsection_lumi,
    weight_pu,
]
