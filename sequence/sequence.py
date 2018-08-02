from . import Modules
from .physics_object_selection import selection_dict

certified_lumi_checker = Modules.CertifiedLumiChecker(
    lumi_json_path = "/vols/build/cms/sdb15/atuproot/data/json/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt",
    mc = False,
)

trigger_checker = Modules.TriggerChecker(
    mc = False,
)

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
gen_boson_producer = Modules.GenBosonProducer(
    data = False,
)

weight_creator = Modules.WeightCreator()
weight_xsection_lumi = Modules.WeightXsLumi(
    data = False,
)
weight_pu = Modules.WeightPileup(
    correction_file = "/vols/build/cms/sdb15/atuproot/data/pileup/nTrueInt_corrections.txt",
    overflow = True, data = False,
)
weight_met_trigger = Modules.WeightMetTrigger(
    correction_files = {
        0: "/vols/build/cms/sdb15/atuproot/data/mettrigger/met_trigger_correction_0mu.txt",
        1: "/vols/build/cms/sdb15/atuproot/data/mettrigger/met_trigger_correction_1mu.txt",
        2: "/vols/build/cms/sdb15/atuproot/data/mettrigger/met_trigger_correction_2mu.txt",
    },
    data = False,
)
weight_muons = Modules.WeightMuons(
    correction_id_paths = [
        (19.7, "/vols/build/cms/sdb15/atuproot/data/muons/muon_id_runBCDEF.txt"),
        (16.2, "/vols/build/cms/sdb15/atuproot/data/muons/muon_id_runGH.txt"),
    ],
    correction_iso_paths = [
        (19.7, "/vols/build/cms/sdb15/atuproot/data/muons/muon_isolation_runBCDEF.txt"),
        (16.2, "/vols/build/cms/sdb15/atuproot/data/muons/muon_isolation_runGH.txt"),
    ],
    correction_track_paths = [
        (1., "/vols/build/cms/sdb15/atuproot/data/muons/muon_tracking.txt"),
    ],
    correction_trig_paths = [
        (19.7, "/vols/build/cms/sdb15/atuproot/data/muons/muon_trigger_runBCDEF.txt"),
        (16.2, "/vols/build/cms/sdb15/atuproot/data/muons/muon_trigger_runGH.txt"),
    ],
    data = False,
)

selection_producer = Modules.SelectionProducer()

sequence = [
    certified_lumi_checker,
    trigger_checker,
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
    weight_met_trigger,
    weight_muons,
    selection_producer,
]
