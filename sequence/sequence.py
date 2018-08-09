from . import Readers
from . import Collectors
from .physics_object_selection import selection_dict
from alphatwirl.loop import NullCollector

certified_lumi_checker = Readers.CertifiedLumiChecker(
    lumi_json_path = "atuproot/data/json/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt",
    mc = False,
)

trigger_checker = Readers.TriggerChecker(
    mc = False,
)

collection_creator = Readers.CollectionCreator(
    name = "collection_creator",
    collections = ["CaloMET", "MET", "Jet", "Electron", "Muon", "Photon",
                   "Tau", "GenMET", "GenPart", "GenJet", "GenDressedLepton"],
)

skim_collections = Readers.SkimCollections(
    name = "skim_collections",
    selection_dict = selection_dict,
)

jet_cross_cleaning = Readers.ObjectCrossCleaning(
    name = "jet_cross_cleaning",
    clean_collections = ("Jet",),
    ref_collections = ("MuonVeto", "ElectronVeto", "PhotonVeto"),
)

tau_cross_cleaning = Readers.ObjectCrossCleaning(
    name = "tau_cross_cleaning",
    clean_collections = ("Tau",),
    ref_collections = ("MuonVeto", "ElectronVeto"),
)

jec_variations = Readers.JecVariations(
    jes_unc_file = "atuproot/data/jecs/Summer16_23Sep2016V4_MC_Uncertainty_AK4PFchs.txt",
    variation = None,
)

event_sums_producer = Readers.EventSumsProducer()
signal_region_blinder = Readers.SignalRegionBlinder(
    blind = True,
)
inv_mass_producer = Readers.InvMassProducer()
gen_boson_producer = Readers.GenBosonProducer(
    data = False,
)

weight_creator = Readers.WeightCreator()
weight_xsection_lumi = Readers.WeightXsLumi(
    data = False,
)
weight_pu = Readers.WeightPileup(
    correction_file = "atuproot/data/pileup/nTrueInt_corrections.txt",
    overflow = True, data = False,
)
weight_met_trigger = Readers.WeightMetTrigger(
    correction_files = {
        0: "atuproot/data/mettrigger/met_trigger_correction_0mu.txt",
        1: "atuproot/data/mettrigger/met_trigger_correction_1mu.txt",
        2: "atuproot/data/mettrigger/met_trigger_correction_2mu.txt",
    },
    data = False,
)
weight_muons = Readers.WeightMuons(
    correction_id_paths = [
        (19.7, "atuproot/data/muons/muon_id_runBCDEF.txt"),
        (16.2, "atuproot/data/muons/muon_id_runGH.txt"),
    ],
    correction_iso_paths = [
        (19.7, "atuproot/data/muons/muon_isolation_runBCDEF.txt"),
        (16.2, "atuproot/data/muons/muon_isolation_runGH.txt"),
    ],
    correction_track_paths = [
        (1., "atuproot/data/muons/muon_tracking.txt"),
    ],
    correction_trig_paths = [
        (19.7, "atuproot/data/muons/muon_trigger_runBCDEF.txt"),
        (16.2, "atuproot/data/muons/muon_trigger_runGH.txt"),
    ],
    data = False,
)

selection_producer = Readers.SelectionProducer()

hist_reader = Collectors.HistReader()
hist_collector = Collectors.HistCollector()

sequence = [
    # Creates object collections accessible through the event variable. e.g.
    # event.Jet.pt rather than event.Jet_pt. Simpler to pass a collection to
    # functions and allows subcollections (done by skim_collections)
    (collection_creator, NullCollector()),
    # Try to keep GenPart branch stuff before everything else. It's quite big
    # and is deleted after use. Don't want to add the memory consumption of
    # this with all other branches
    (gen_boson_producer, NullCollector()),
    (jec_variations, NullCollector()),
    (skim_collections, NullCollector()),
    # Cross cleaning must be placed after the veto and selection collections
    # are created but before they're used anywhere to allow the collection
    # selection mask to be updated
    (jet_cross_cleaning, NullCollector()),
    (tau_cross_cleaning, NullCollector()),
    # General event variable producers
    (event_sums_producer, NullCollector()),
    (inv_mass_producer, NullCollector()),
    # Readers which create a mask for the event. Doesn't apply it, just stores
    # the mask as an array of booleans
    (trigger_checker, NullCollector()),
    (certified_lumi_checker, NullCollector()),
    (signal_region_blinder, NullCollector()),
    (selection_producer, NullCollector()),
    # Weighters. Need to add a weight (of ones) to the event first -
    # weight_creator. The generally just apply to MC and that logic it dealt
    # with by the ScribblerWrapper.
    (weight_creator, NullCollector()),
    (weight_xsection_lumi, NullCollector()),
    (weight_pu, NullCollector()),
    (weight_met_trigger, NullCollector()),
    (weight_muons, NullCollector()),
    # Add collectors (with accompanying readers) at the end so that all
    # event attributes are available to them
    (hist_reader, hist_collector),
]
