import numpy as np
import os
import pickle
import logging

from utils.Lambda import Lambda
from drawing.dist_ratio import dist_ratio

class HistReader(object):
    def __init__(self, cfg=None):
        """
        Get the list of histogram configs and expand them for 1 histogram per
        entry (i.e. unroll the cutflows)

        Also create empty dict for lambda functions later
        """
        self.histogrammer_cfgs = cfg.histogrammer_cfgs

        self.histogram_cfgs = []
        self.functions = []
        for hist_cfg in self.histogrammer_cfgs:
            for cutflow in hist_cfg["cutflows"]:
                self.histogram_cfgs.append({
                    "name": (cutflow, hist_cfg["name"]),
                    "variables": hist_cfg["variables"],
                    "bins": hist_cfg["bins"],
                    "weight": hist_cfg["weight"],
                })
                for variable in hist_cfg["variables"]+[hist_cfg["weight"]]:
                    if variable not in self.functions:
                        self.functions.append(variable)

        self.string_conv_func = {}

    def begin(self, event):
        """
        Create empty dict to store the histograms. The histogram name is unique

        Create the lambda functions
        """
        self.dataset = event.config.dataset
        self.histograms = {}

        for function in self.functions:
            self.string_conv_func[function] = Lambda(function)

    def end(self):
        """
        Remove unpicklabe lambda functions
        """
        self.string_conv_func = {}

    def event(self, event):
        """
        Loop over event blocks and histogramming them.

        Add together the histograms from different blocks.
        """
        for histogram_cfg in self.histogram_cfgs:
            cutflow = histogram_cfg["name"][0]
            weight = histogram_cfg["weight"]

            selection = getattr(event, "Cutflow_{}".format(cutflow))
            weights = self.string_conv_func[weight](event)[selection]

            variables = [self.string_conv_func[variable](event)[selection]
                         for variable in histogram_cfg["variables"]]
            bins = histogram_cfg["bins"]
            weights1 = [weights]*len(variables)
            weights2 = [weights**2]*len(variables)

            if len(variables) == 1:
                variables = variables[0]
                bins = bins[0]
                weights1 = weights1[0]
                weights2 = weights2[0]

            hist_counts, hist_bins = np.histogram(variables, bins=bins)
            hist_yields = np.histogram(variables, bins=bins, weights=weights1)[0]
            hist_variance = np.histogram(variables, bins=bins, weights=weights2)[0]

            identifier = histogram_cfg["name"]
            if identifier not in self.histograms:
                self.histograms[identifier] = {
                    "bins": hist_bins,
                    "counts": hist_counts,
                    "yields": hist_yields,
                    "variance": hist_variance,
                }
            else:
                histogram = self.histograms[identifier]
                self.histograms[identifier] = {
                    "bins": histogram["bins"],
                    "counts": histogram["counts"] + hist_counts,
                    "yields": histogram["yields"] + hist_yields,
                    "variance": histogram["variance"] + hist_variance,
                }

    def merge(self, other):
        """
        Merge histograms from different (computational) processes
        """
        for identifier in self.histograms:
            other_hists = other.histograms[identifier]
            self_hists = self.histograms[identifier]

            self.histograms[identifier] = {
                "bins": self_hists["bins"],
                "counts": self_hists["counts"] + other_hists["counts"],
                "yields": self_hists["yields"] + other_hists["yields"],
                "variance": self_hists["variance"] + other_hists["variance"],
            }

class HistCollector(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.outdir = "output"
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

    def collect(self, dataset_readers_list):
        """
        Add together the histograms into dataset parents. Pass the results to
        the plotting scripts to draw it
        """
        histograms = {}
        for dataset, readers in dataset_readers_list:
            parent = readers[0].dataset.parent

            for identifier, old_histogram in readers[0].histograms.items():
                new_identifier = (identifier[0], parent, identifier[1])
                if new_identifier in histograms:
                    histogram = histograms[new_identifier]
                    histograms[new_identifier] = {
                        "bins": histogram["bins"],
                        "counts": old_histogram["counts"] + histogram["counts"],
                        "yields": old_histogram["yields"] + histogram["yields"],
                        "variance": old_histogram["variance"] + histogram["variance"],
                    }
                else:
                    histograms[new_identifier] = {
                        "bins": old_histogram["bins"],
                        "counts": old_histogram["counts"],
                        "yields": old_histogram["yields"],
                        "variance": old_histogram["variance"],
                    }

        for (cutflow, parent, histname), histogram in histograms.items():
            outdir = os.path.join(self.outdir, cutflow, parent)
            if not os.path.exists(outdir):
                os.makedirs(outdir)

            path = os.path.join(outdir, histname+".pkl")
            with open(path, 'w') as f:
                pickle.dump(histogram, f)

        self.draw(histograms)
        return dataset_readers_list

    def draw(self, histograms):
        """
        Setup everything required for the drawing function
        """
        logger = logging.getLogger(__name__)
        cutflow_histnames = list(set([(k[0], k[2]) for k in histograms]))

        for cutflow, histname in cutflow_histnames:
            for data_parent in ["MET", "SingleMuon"]:
                key = (cutflow, data_parent, histname)
                if key not in histograms:
                    logger.warning("{} not in output".format(key))
                    continue
                histogram = histograms[key]

                hist_data = {
                    "name": histname,
                    "sample": data_parent,
                    "bins": histogram["bins"],
                    "counts": histogram["counts"],
                    "yields": histogram["yields"],
                    "variance": histogram["variance"],
                }

                try:
                    hists_mc = [{
                        "name": histname,
                        "sample": mc_parent,
                        "bins": histograms[(cutflow, mc_parent, histname)]["bins"],
                        "counts": histograms[(cutflow, mc_parent, histname)]["counts"],
                        "yields": histograms[(cutflow, mc_parent, histname)]["yields"],
                        "variance": histograms[(cutflow, mc_parent, histname)]["variance"],
                    } for mc_parent in ['DYJetsToLL', 'Diboson', 'EWKV2Jets',
                                        'G1Jet', 'QCD', 'SingleTop', 'TTJets',
                                        'VGamma', 'WJetsToLNu', 'ZJetsToNuNu']]
                except KeyError:
                    for mc_parent in ['DYJetsToLL', 'Diboson', 'EWKV2Jets',
                                      'G1Jet', 'QCD', 'SingleTop', 'TTJets',
                                      'VGamma', 'WJetsToLNu', 'ZJetsToNuNu']:
                        key = (cutflow, mc_parent, histname)
                        if key not in histograms:
                            logger.warning("{} not in output".format(key))
                    continue

                path = os.path.join(self.outdir, cutflow, "plots", data_parent)
                if not os.path.exists(path):
                    os.makedirs(path)

                dist_ratio(
                    hist_data,
                    hists_mc,
                    os.path.join(path, histname),
                    self.cfg,
                )

    def reread(self, outdir):
        """
        Reread the output pickle files to recreate the pdf plots created from
        them.
        """
        logger = logging.getLogger(__name__)
        histograms = {}
        for cutflow in os.listdir(outdir):
            for parent in os.listdir(os.path.join(outdir, cutflow)):
                if parent == "plots":
                    continue
                for histpath in os.listdir(os.path.join(outdir, cutflow, parent)):
                    histname = os.path.splitext(os.path.basename(histpath))[0]
                    key = (cutflow, parent, histname)
                    if key in histograms:
                        logger.warning("{} already loaded".format(key))
                        continue
                    with open(os.path.join(outdir, cutflow, parent, histpath), 'r') as f:
                        histograms[key] = pickle.load(f)
        self.draw(histograms)
        return histograms
