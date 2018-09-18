import Readers
import Collectors
from event_selection import event_selection
from physics_object_selection import physics_object_selection
from alphatwirl.loop import NullCollector

import os
datapath = os.path.join(os.environ["TOPDIR"], "data")
#print(datapath)

certified_lumi_checker = Readers.CertifiedLumiChecker(
    name = "certified_lumi_checker",
    lumi_json_path = datapath + "/json/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt",
    mc = False,
)

trigger_checker = Readers.TriggerChecker(
    name = "trigger_checker",
    mc = False,
)

collection_creator = Readers.CollectionCreator(
    name = "collection_creator",
    collections = ["CaloMET", "MET", "Jet", "Electron", "Muon", "Photon", "Tau",
                   "GenMET", "GenPart", "GenJet", "GenDressedLepton", "LHEPart"],
)

skim_collections = Readers.SkimCollections(
    name = "skim_collections",
    selection_dict = physics_object_selection.selection_dict,
)

jet_cross_cleaning = Readers.ObjectCrossCleaning(
    name = "jet_cross_cleaning",
    collections = ("Jet",),
    ref_collections = ("MuonVeto", "ElectronVeto", "PhotonVeto"),
)

tau_cross_cleaning = Readers.ObjectCrossCleaning(
    name = "tau_cross_cleaning",
    collections = ("Tau",),
    ref_collections = ("MuonVeto", "ElectronVeto"),
)

jec_variations = Readers.JecVariations(
    name = "jec_variations",
    jes_unc_file = datapath + "/jecs/Summer16_23Sep2016V4_MC_Uncertainty_AK4PFchs.txt",
    jer_sf_file = datapath + "/jecs/Spring16_25nsV10a_MC_SF_AK4PFchs.txt",
    jer_file = datapath + "/jecs/Spring16_25nsV10_MC_PtResolution_AK4PFchs.txt",
    variation = None,
)

event_sums_producer = Readers.EventSumsProducer(
    name = "event_sums_producer",
)
signal_region_blinder = Readers.SignalRegionBlinder(
    name = "signal_region_blinder",
    blind = True,
    apply_to_mc = False,
)
inv_mass_producer = Readers.InvMassProducer(
    name = "inv_mass_producer",
)
gen_boson_producer = Readers.GenBosonProducer(
    name = "gen_boson_producer",
    data = False,
)
lhe_part_assigner = Readers.LHEPartAssigner(
    name = "lhe_part_assigner",
    data = False,
)

weight_creator = Readers.WeightCreator(
    name = "weight_creator",
)
weight_xsection_lumi = Readers.WeightXsLumi(
    name = "weight_xsection_lumi",
    data = False,
)
weight_pu = Readers.WeightPileup(
    name = "weight_pu",
    correction_file = datapath + "/pileup/nTrueInt_corrections.txt",
    overflow = True,
    data = False,
)
weight_met_trigger = Readers.WeightMetTrigger(
    name = "weight_met_trigger",
    correction_files = {
        0: datapath + "/mettrigger/met_trigger_correction_0mu.txt",
        1: datapath + "/mettrigger/met_trigger_correction_1mu.txt",
        2: datapath + "/mettrigger/met_trigger_correction_2mu.txt",
    },
    data = False,
)
weight_muons = Readers.WeightMuons(
    name = "weight_muons",
    correction_id_paths = [
        (19.7, datapath + "/muons/muon_id_runBCDEF.txt"),
        (16.2, datapath + "/muons/muon_id_runGH.txt"),
    ],
    correction_iso_paths = [
        (19.7, datapath + "/muons/muon_isolation_runBCDEF.txt"),
        (16.2, datapath + "/muons/muon_isolation_runGH.txt"),
    ],
    correction_track_paths = [
        (1., datapath + "/muons/muon_tracking.txt"),
    ],
    correction_trig_paths = [
        (19.7, datapath + "/muons/muon_trigger_runBCDEF.txt"),
        (16.2, datapath + "/muons/muon_trigger_runGH.txt"),
    ],
    data = False,
)
weight_qcd_ewk = Readers.WeightQcdEwk(
    name = "weight_qcd_ewk",
    formula = "kappa_EW: (1+kappa_EW)",
    #formula = "K_NLO, K_NNLO, kappa_EW: (K_NNLO/K_NLO)*(1+kappa_EW)",
    input_paths = {
        "ZJetsToNuNu": {
            #"K_NLO": (datapath + "/qcd_ewk/vvj.dat", "vvj_pTV_K_NLO"),
            #"K_NNLO": (datapath + "/qcd_ewk/eej.dat", "eej_pTV_K_NNLO"),
            "kappa_EW": (datapath + "/qcd_ewk/vvj.dat", "vvj_pTV_kappa_EW"),
        },
        "WJetsToLNu": {
            #"K_NLO": (datapath + "/qcd_ewk/evj.dat", "evj_pTV_K_NLO"),
            #"K_NNLO": (datapath + "/qcd_ewk/evj.dat", "evj_pTV_K_NNLO"),
            "kappa_EW": (datapath + "/qcd_ewk/evj.dat", "evj_pTV_kappa_EW"),
        },
        "DYJetsToLL": {
            #"K_NLO": (datapath + "/qcd_ewk/eej.dat", "eej_pTV_K_NLO"),
            #"K_NNLO": (datapath + "/qcd_ewk/eej.dat", "eej_pTV_K_NNLO"),
            "kappa_EW": (datapath + "/qcd_ewk/eej.dat", "eej_pTV_kappa_EW"),
        },
    },
)

selection_producer = Readers.SelectionProducer(
    name = "selection_producer",
    event_selection = event_selection,
)

hist_reader = Collectors.HistReader(
    name = "hist_reader",
    cfg = Collectors.Histogrammer_cfg,
)
hist_collector = Collectors.HistCollector(
    name = "hist_collector",
    plot = True,
    cfg = Collectors.Histogrammer_cfg,
)

gen_stitching_reader = Collectors.GenStitchingReader(
    name = "gen_stitching_reader",
    cfg = Collectors.GenStitching_cfg,
)
gen_stitching_collector = Collectors.GenStitchingCollector(
    name = "gen_stitching_collector",
    plot = True,
    cfg = Collectors.GenStitching_cfg,
)

import numpy as np
for cfg in Collectors.MetResponseResolution_cfg.histogrammer_cfgs:
    cfg["bins"][1] = [-np.infty, 0., 20., 26., 32., 38., 44., 50., 60., 70.,
                      80., 90., 100., 116., 132., 150., 175., 200., 225., 250.,
                      275., 305., 335., 365., 400., 450., np.infty]
met_response_resolution_reader = Collectors.MetResponseResolutionReader(
    name = "met_response_resolution_reader",
    cfg = Collectors.MetResponseResolution_cfg,
)
met_response_resolution_collector = Collectors.MetResponseResolutionCollector(
    name = "met_response_resolution_collector",
    plot = True,
    cfg = Collectors.MetResponseResolution_cfg,
)

qcd_ewk_corrections_reader = Collectors.QcdEwkCorrectionsReader(
    name = "qcd_ewk_corrections_reader",
    cfg = Collectors.QcdEwkCorrections_cfg,
)
qcd_ewk_corrections_collector = Collectors.QcdEwkCorrectionsCollector(
    name = "qcd_ewk_corrections_collector",
    plot = True,
    cfg = Collectors.QcdEwkCorrections_cfg,
)

systematics_reader = Collectors.SystematicsReader(
    name = "systematics_reader",
    cfg = Collectors.Systematics_cfg,
)
systematics_collector = Collectors.SystematicsCollector(
    name = "systematics_collector",
    plot = True,
    cfg = Collectors.Systematics_cfg,
)

sequence = [
    # Creates object collections accessible through the event variable. e.g.
    # event.Jet.pt rather than event.Jet_pt. Simpler to pass a collection to
    # functions and allows subcollections (done by skim_collections)
    (collection_creator, NullCollector()),
    # Try to keep GenPart branch stuff before everything else. It's quite big
    # and is deleted after use. Don't want to add the memory consumption of
    # this with all other branches
    (gen_boson_producer, NullCollector()),
    (lhe_part_assigner, NullCollector()),
    #(jec_variations, NullCollector()),
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
    # Weighters. Need to add a weight (of ones) to the event first -
    # weight_creator. The generally just apply to MC and that logic it dealt
    # with by the ScribblerWrapper.
    (weight_creator, NullCollector()),
    (weight_xsection_lumi, NullCollector()),
    (weight_pu, NullCollector()),
    (weight_met_trigger, NullCollector()),
    (weight_muons, NullCollector()),
    (weight_qcd_ewk, NullCollector()),
    (selection_producer, NullCollector()),
    # Add collectors (with accompanying readers) at the end so that all
    # event attributes are available to them
    (hist_reader, hist_collector),
    (gen_stitching_reader, gen_stitching_collector),
    (met_response_resolution_reader, met_response_resolution_collector),
    (qcd_ewk_corrections_reader, qcd_ewk_corrections_collector),
    (systematics_reader, systematics_collector),
]
