lumi_selection = "ev: ev.IsCertified"
trigger_selection = "ev: ev.IsTriggered"
filter_selection = "ev: (ev.Flag_goodVertices>0.5) & "\
                       "(ev.Flag_globalTightHalo2016Filter>0.5) & "\
                       "(ev.Flag_HBHENoiseFilter>0.5) & "\
                       "(ev.Flag_HBHENoiseIsoFilter>0.5) & "\
                       "(ev.Flag_EcalDeadCellTriggerPrimitiveFilter>0.5) & "\
                       "(ev.Flag_eeBadScFilter>0.5)"
met_selection = "ev: ev.METnoX.pt > 200."
dphi_jet_met_selection = "ev: ev.MinDPhiJ1234METnoX > 0.5"
dphi_jet_met_inv_selection = "ev: ev.MinDPhiJ1234METnoX <= 0.5"
dcalo_pfmet_selection = "ev: ev.MET_dCaloMET < 0.5"
jet_selection = "ev: (ev.JetSelection.size > 0) & "\
                    "(ev.JetSelection.size == ev.JetVeto.size) & "\
                    "(ev.LeadJetSelection.chHEF > 0.1) & "\
                    "(ev.LeadJetSelection.chHEF < 0.95)"
muon_selection = "ev: (ev.MuonSelection.size == ev.MuonVeto.size) & (ev.MuonVeto.size == {})"
ele_selection = "ev: (ev.ElectronSelection.size == ev.ElectronVeto.size) & (ev.ElectronVeto.size == {})"
pho_veto = "ev: (ev.PhotonSelection.size == ev.PhotonVeto.size) & (ev.PhotonVeto.size == 0)"
nbjet_veto = "ev: (ev.nBJetSelectionMedium == 0)"
tau_veto = "ev: (ev.TauSelection.size == ev.TauVeto.size) & (ev.TauVeto.size == 0)"
mtw_selection = "ev: (ev.MTW >= 30.) & (ev.MTW < 125.)"
mll_selection = "ev: (ev.MLL >= 71.) & (ev.MLL < 111.)"

large_weight_removal = "ev: (ev.Weight_MET<100.) & (ev.Weight_SingleMuon<100.)"
ngen_boson_selection = "ev: True if ev.config.parent not in 'EWKV2Jets' else (ev.nGenBosons==1)"

blind_mask = "ev: ev.BlindMask"
metsb_selection = "ev: ev.METnoX.pt <= 250."
metsr_selection = "ev: ev.METnoX.pt > 250."

# Selections
data_selection = [
    ("lumi_selection", lumi_selection),
    ("trigger_selection", trigger_selection),
]

mc_selection = []

baseline_selection = [
    ("filter_selection", filter_selection),
    ("met_selection", met_selection),
    ("dcalo_pfmet_selection", dcalo_pfmet_selection),
    ("jet_selection", jet_selection),
    ("pho_veto", pho_veto),
    ("nbjet_veto", nbjet_veto),
    ("tau_veto", tau_veto),
    ("large_weight_removal", large_weight_removal),
]

monojet_selection = [
    ("blind_mask", blind_mask),
    ("dphi_jet_met_selection", dphi_jet_met_selection),
    ("muon_selection_fmt_0", muon_selection.format(0)),
    ("ele_selection_fmt_0", ele_selection.format(0)),
]
monojetsb_selection = [
    ("metsb_selection", metsb_selection),
    ("dphi_jet_met_selection", dphi_jet_met_selection),
    ("muon_selection_fmt_0", muon_selection.format(0)),
    ("ele_selection_fmt_0", ele_selection.format(0)),
]
monojetsr_selection = [
    ("blind_mask", blind_mask),
    ("metsr_selection", metsr_selection),
    ("dphi_jet_met_selection", dphi_jet_met_selection),
    ("muon_selection_fmt_0", muon_selection.format(0)),
    ("ele_selection_fmt_0", ele_selection.format(0)),
]

singlemuon_selection = [
    ("dphi_jet_met_selection", dphi_jet_met_selection),
    ("muon_selection_fmt_1", muon_selection.format(1)),
    ("ele_selection_fmt_0", ele_selection.format(0)),
    ("mtw_selection", mtw_selection),
]
singlemuonsb_selection = [
    ("metsb_selection", metsb_selection),
    ("dphi_jet_met_selection", dphi_jet_met_selection),
    ("muon_selection_fmt_1", muon_selection.format(1)),
    ("ele_selection_fmt_0", ele_selection.format(0)),
    ("mtw_selection", mtw_selection),
]
singlemuonsr_selection = [
    ("metsr_selection", metsr_selection),
    ("dphi_jet_met_selection", dphi_jet_met_selection),
    ("muon_selection_fmt_1", muon_selection.format(1)),
    ("ele_selection_fmt_0", ele_selection.format(0)),
    ("mtw_selection", mtw_selection),
]

doublemuon_selection = [
    ("blind_mask", blind_mask),
    ("dphi_jet_met_selection", dphi_jet_met_selection),
    ("muon_selection_fmt_2", muon_selection.format(2)),
    ("ele_selection_fmt_0", ele_selection.format(0)),
    ("mll_selection", mll_selection),
]
doublemuonsb_selection = [
    ("metsb_selection", metsb_selection),
    ("dphi_jet_met_selection", dphi_jet_met_selection),
    ("muon_selection_fmt_2", muon_selection.format(2)),
    ("ele_selection_fmt_0", ele_selection.format(0)),
    ("mll_selection", mll_selection),
]
doublemuonsr_selection = [
    ("blind_mask", blind_mask),
    ("metsr_selection", metsr_selection),
    ("dphi_jet_met_selection", dphi_jet_met_selection),
    ("muon_selection_fmt_2", muon_selection.format(2)),
    ("ele_selection_fmt_0", ele_selection.format(0)),
    ("mll_selection", mll_selection),
]

singleelectron_selection = [
    ("dphi_jet_met_selection", dphi_jet_met_selection),
    ("muon_selection_fmt_0", muon_selection.format(0)),
    ("ele_selection_fmt_1", ele_selection.format(1)),
    ("mtw_selection", mtw_selection),
]
singleelectronsb_selection = [
    ("metsb_selection", metsb_selection),
    ("dphi_jet_met_selection", dphi_jet_met_selection),
    ("muon_selection_fmt_0", muon_selection.format(0)),
    ("ele_selection_fmt_1", ele_selection.format(1)),
    ("mtw_selection", mtw_selection),
]
singleelectronsr_selection = [
    ("metsr_selection", metsr_selection),
    ("dphi_jet_met_selection", dphi_jet_met_selection),
    ("muon_selection_fmt_0", muon_selection.format(0)),
    ("ele_selection_fmt_1", ele_selection.format(1)),
    ("mtw_selection", mtw_selection),
]

doubleelectron_selection = [
    ("dphi_jet_met_selection", dphi_jet_met_selection),
    ("muon_selection_fmt_0", muon_selection.format(0)),
    ("ele_selection_fmt_2", ele_selection.format(2)),
    ("mll_selection", mll_selection),
]
doubleelectronsb_selection = [
    ("metsb_selection", metsb_selection),
    ("dphi_jet_met_selection", dphi_jet_met_selection),
    ("muon_selection_fmt_0", muon_selection.format(0)),
    ("ele_selection_fmt_2", ele_selection.format(2)),
    ("mll_selection", mll_selection),
]
doubleelectronsr_selection = [
    ("metsr_selection", metsr_selection),
    ("dphi_jet_met_selection", dphi_jet_met_selection),
    ("muon_selection_fmt_0", muon_selection.format(0)),
    ("ele_selection_fmt_2", ele_selection.format(2)),
    ("mll_selection", mll_selection),
]

monojetqcd_selection = [
    ("dphi_jet_met_inv_selection", dphi_jet_met_inv_selection),
    ("muon_selection_fmt_0", muon_selection.format(0)),
    ("ele_selection_fmt_0", ele_selection.format(0)),
]
monojetqcdsb_selection = [
    ("metsb_selection", metsb_selection),
    ("dphi_jet_met_inv_selection", dphi_jet_met_inv_selection),
    ("muon_selection_fmt_0", muon_selection.format(0)),
    ("ele_selection_fmt_0", ele_selection.format(0)),
]
monojetqcdsr_selection = [
    ("metsr_selection", metsr_selection),
    ("dphi_jet_met_inv_selection", dphi_jet_met_inv_selection),
    ("muon_selection_fmt_0", muon_selection.format(0)),
    ("ele_selectio_fmt_0", ele_selection.format(0)),
]
