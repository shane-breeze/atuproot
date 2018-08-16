from collections import namedtuple
import logging
import numpy as np
import os
import pickle

from utils.Lambda import Lambda
from drawing.dist_ratio import dist_ratio

from utils.Histogramming import Histogram, Histograms

# Take the cfg module and drop unpicklables
Config = namedtuple("Config", "histogrammer_cfgs sample_colours axis_label")

class HistReader(object):
    def __init__(self, **kwargs):
        cfg = kwargs.pop("cfg")
        self.cfg = Config(
            histogrammer_cfgs = cfg.histogrammer_cfgs,
            sample_colours = cfg.sample_colours,
            axis_label = cfg.axis_label,
        )
        self.split_lepton_decays = True
        self.__dict__.update(kwargs)

        # convert cfg to histogram classes
        configs = []
        for cfg in self.cfg.histogrammer_cfgs:
            # expand categories
            for dataset, cutflow in cfg["categories"]:
                cutflow_restriction = "ev: ev.Cutflow_{}".format(cutflow)
                selection = [cutflow_restriction]
                weight = "ev: ev.Weight_{}".format(dataset)
                if "additional_weights" in cfg:
                    weight += " * ".join(cfg["additional_weights"])
                identifier = (dataset, cutflow, None, cfg["name"])

                configs.append({
                    "identifier": identifier,
                    "hist_config": {
                        "name": cfg["name"],
                        "variables": cfg["variables"],
                        "bins": cfg["bins"],
                        "weight": weight,
                        "selection": selection,
                    },
                })

        self.histograms = Histograms()
        self.histograms.extend([
            (config["identifier"], Histogram(**config["hist_config"]))
            for config in configs
        ])

    def begin(self, event):
        self.histograms.begin(event)

    def end(self):
        self.histograms.end()

    def event(self, event):
        self.histograms.event(event)

    def merge(self, other):
        self.histograms.merge(other.histograms)

class HistCollector(object):
    def __init__(self, **kwargs):
        # drop unpicklables
        cfg = kwargs.pop("cfg")
        self.cfg = Config(
            histogrammer_cfgs = cfg.histogrammer_cfgs,
            sample_colours = cfg.sample_colours,
            axis_label = cfg.axis_label,
        )
        self.__dict__.update(kwargs)

        self.outdir = os.path.join("output", self.name)
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

    def collect(self, dataset_readers_list):
        histograms = None
        for dataset, readers in dataset_readers_list:
            if histograms is None:
                histograms = readers[0].histograms
            else:
                histograms.merge(readers[0].histograms)
        histograms.save(self.outdir)
        #self.draw(histograms)
        return dataset_readers_list

#    def draw(self, histograms):
#        """
#        Setup everything required for the drawing function
#        """
#        logger = logging.getLogger(__name__)
#        cutflow_histnames = list(set([(k[0], k[2]) for k in histograms]))
#
#        for cutflow, histname in cutflow_histnames:
#            for data_parent in ["MET", "SingleMuon"]:
#                key = (cutflow, data_parent, histname)
#                if key not in histograms:
#                    logger.warning("{} not in output".format(key))
#                    continue
#                histogram = histograms[key]
#
#                hist_data = {
#                    "name": histname,
#                    "sample": data_parent,
#                    "bins": histogram["bins"],
#                    "counts": histogram["counts"],
#                    "yields": histogram["yields"],
#                    "variance": histogram["variance"],
#                }
#
#                try:
#                    hists_mc = [{
#                        "name": histname,
#                        "sample": mc_parent,
#                        "bins": histograms[(cutflow, mc_parent, histname)]["bins"],
#                        "counts": histograms[(cutflow, mc_parent, histname)]["counts"],
#                        "yields": histograms[(cutflow, mc_parent, histname)]["yields"],
#                        "variance": histograms[(cutflow, mc_parent, histname)]["variance"],
#                    } for mc_parent in ['DYJetsToEE', 'DYJetsToMuMu', 'DYJetsToTauTau',
#                                        'WJetsToENu', 'WJetsToMuNu', 'WJetsToTauNu',
#                                        'ZJetsToNuNu', 'TTJets', 'SingleTop',
#                                        'QCD', 'Diboson', 'EWKV2Jets',
#                                        'G1Jet', 'VGamma']]
#                except KeyError:
#                    for mc_parent in ['DYJetsToEE', 'DYJetsToMuMu', 'DYJetsToTauTau',
#                                      'WJetsToENu', 'WJetsToMuNu', 'WJetsToTauNu',
#                                      'ZJetsToNuNu', 'TTJets', 'SingleTop',
#                                      'QCD', 'Diboson', 'EWKV2Jets',
#                                      'G1Jet', 'VGamma']:
#                        key = (cutflow, mc_parent, histname)
#                        if key not in histograms:
#                            logger.warning("{} not in output".format(key))
#                    continue
#
#                path = os.path.join(self.outdir, self.name, cutflow, "plots", data_parent)
#                if not os.path.exists(path):
#                    os.makedirs(path)
#
#                #dist_ratio(
#                #    hist_data,
#                #    hists_mc,
#                #    os.path.join(path, histname),
#                #    self.cfg,
#                #)

    def reload(self, outdir):
        self.histograms = Histograms()
        self.histograms.reload(outdir)
        #self.draw(histograms)
        return self.histograms
