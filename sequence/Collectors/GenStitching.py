import os

from drawing.dist_stitch import dist_stitch
from utils.Histogramming import Histogram, Histograms

from Histogrammer import Config, HistReader, HistCollector

class GenStitchingReader(HistReader):
    def __init__(self, **kwargs):
        cfg = kwargs.pop("cfg")
        self.cfg = Config(
            sample_names = cfg.sample_names,
            sample_colours = cfg.sample_colours,
            axis_label = cfg.axis_label,
            log = True,
        )
        self.split_lepton_decays = True
        self.__dict__.update(kwargs)

        weight = "ev: ev.Weight_XsLumi"
        self.split_samples = {}

        # convert cfg to histogram classes
        configs = []
        for cfg in cfg.histogrammer_cfgs:
            # expand categories
            for parent in cfg["categories"]:
                identifier = (parent, "None", None, cfg["name"])

                configs.append({
                    "identifier": identifier,
                    "hist_config": {
                        "name": cfg["name"],
                        "variables": cfg["variables"],
                        "bins": cfg["bins"],
                        "weight": weight,
                        "selection": [],
                    },
                })

        self.histograms = Histograms()
        self.histograms.extend([
            (config["identifier"], Histogram(**config["hist_config"]))
            for config in configs
        ])

        # Normalisation factor (i.e. sum of weighted events). Sample dependent
        # for the correct pre-selection XS
        self.normalisation = {}

    def begin(self, event):
        parent = event.config.dataset.name.split("_ext")[0]
        self.parents = [parent]
        selection = {}
        self.histograms.begin(event, self.parents, selection)

class GenStitchingCollector(HistCollector):
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
            path = os.path.join(self.outdir, dataset, cutflow)
            if not os.path.exists(path):
                os.makedirs(path)
            filepath = os.path.abspath(os.path.join(path, histname))

            hists_mc = []
            for n, h in histograms.histograms:
                if (n[0], n[1], n[3]) != (dataset, cutflow, histname):
                    continue

                if dataset not in n[2]:
                    continue

                plot_item = {
                    "name": n[3],
                    "sample": n[2],
                    "bins": h.histogram["bins"],
                    "counts": h.histogram["counts"],
                    "yields": h.histogram["yields"],
                    "variance": h.histogram["variance"],
                }
                hists_mc.append(plot_item)

            args.append([hists_mc, filepath, self.cfg])

        self.parallel.parallel_mode = "multiprocessing"
        self.parallel.map(dist_stitch, args)

        return histograms
