import os
import operator

from drawing.dist_ratio import dist_ratio
from utils.Histogramming import Histogram, Histograms

# Take the cfg module and drop unpicklables
class Config(object):
    def __init__(self, sample_names=[], sample_colours=[], axis_label=[], log=False):
        self.sample_names = sample_names
        self.sample_colours = sample_colours
        self.axis_label = axis_label
        self.log = log

class HistReader(object):
    split_samples = {
        "DYJetsToLL": {
            "DYJetsToEE": ["ev: ev.LeptonIsElectron"],
            "DYJetsToMuMu": ["ev: ev.LeptonIsMuon"],
            "DYJetsToTauTau": ["ev: ev.LeptonIsTau"],
        },
        "WJetsToLNu": {
            "WJetsToENu": ["ev: ev.LeptonIsElectron"],
            "WJetsToMuNu": ["ev: ev.LeptonIsMuon"],
            "WJetsToTauNu": ["ev: ev.LeptonIsTau"],
        },
    }
    def __init__(self, **kwargs):
        cfg = kwargs.pop("cfg")
        self.cfg = Config(
            sample_names = cfg.sample_names,
            sample_colours = cfg.sample_colours,
            axis_label = cfg.axis_label,
            log = True,
        )
        self.__dict__.update(kwargs)
        self.histograms = self.create_histograms(cfg)

    def create_histograms(self, cfg):
        configs = []
        for cfg in cfg.histogrammer_cfgs:
            # expand categories
            for dataset, cutflow in cfg["categories"]:
                cutflow_restriction = "ev: ev.Cutflow_{}".format(cutflow)
                selection = [cutflow_restriction]
                for weightname, weight in cfg["weights"]:
                    weight = weight.format(dataset=dataset)
                    identifier = (dataset, cutflow, None, cfg["name"], weightname)

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

        # Histograms collection
        histograms = Histograms()
        histograms.extend([
            (config["identifier"], Histogram(**config["hist_config"]))
            for config in configs
        ])
        return histograms

    def begin(self, event):
        parent = event.config.dataset.parent
        self.parents = self.split_samples[parent].keys() \
                       if parent in self.split_samples \
                       else [parent]
        selection = self.split_samples[parent] \
                    if parent in self.split_samples \
                    else {}
        self.histograms.begin(event, self.parents, selection)

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
            sample_names = cfg.sample_names,
            sample_colours = cfg.sample_colours,
            axis_label = cfg.axis_label,
            log = True,
        )
        self.__dict__.update(kwargs)

        self.outdir = os.path.join("output", self.name)
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

    def collect(self, dataset_readers_list):
        histograms = None
        for dataset, readers in dataset_readers_list:
            # Get histograms
            if histograms is None:
                histograms = readers[0].histograms
            else:
                histograms.merge(readers[0].histograms)

        histograms.save(self.outdir)
        if self.plot:
            try:
                return self.draw(histograms)
            except Exception as e:
                print(e)
        return []

    def draw(self, histograms):
        datasets = list(set(
            n[0] for n, _ in histograms.histograms
        ))

        # Set and sort to get all unique combinations of (dataset, cutflow, histname)
        dataset_cutflow_histnames = set(
            (n[0], n[1], n[3]) for n, _ in histograms.histograms
        )
        dataset_cutflow_histnames = sorted(
            dataset_cutflow_histnames, key=operator.itemgetter(2, 1, 0),
        )

        args = []
        for dataset, cutflow, histname in dataset_cutflow_histnames:
            if "remove" in cutflow:
                path = os.path.join(self.outdir, dataset, cutflow.split("_remove_")[0], "removes")
            else:
                path = os.path.join(self.outdir, dataset, cutflow)
            if not os.path.exists(path):
                os.makedirs(path)
            filepath = os.path.abspath(os.path.join(path, histname))

            hist_data = None
            hists_mc = []
            for n, h in histograms.histograms:
                if (n[0], n[1], n[3]) != (dataset, cutflow, histname):
                    continue

                if n[2] in datasets and dataset != n[2]:
                    continue

                if n[2] in ["MET", "SingleMuon", "SingleElectron"] and dataset != n[2]:
                    continue

                plot_item = {
                    "name": n[3],
                    "sample": n[2],
                    "bins": h.histogram["bins"],
                    "counts": h.histogram["counts"],
                    "yields": h.histogram["yields"],
                    "variance": h.histogram["variance"],
                }
                if n[2] == dataset:
                    hist_data = plot_item
                else:
                    hists_mc.append(plot_item)

            args.append([hist_data, hists_mc, filepath, self.cfg])
        return [(dist_ratio, arg) for arg in args]

    def reload(self, outdir):
        histograms = Histograms()
        histograms.reload(os.path.join(outdir, self.name))
        return self.draw(histograms)
