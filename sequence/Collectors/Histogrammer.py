import os
from atuproot.build_parallel import build_parallel

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

        # convert cfg to histogram classes
        configs = []
        for cfg in cfg.histogrammer_cfgs:
            # expand categories
            for dataset, cutflow in cfg["categories"]:
                cutflow_restriction = "ev: ev.Cutflow_{}".format(cutflow)
                selection = [cutflow_restriction]
                weight = cfg["weight"].format(dataset=dataset)
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

        # Histograms collection
        self.histograms = Histograms()
        self.histograms.extend([
            (config["identifier"], Histogram(**config["hist_config"]))
            for config in configs
        ])

        # Normalisation factor (i.e. sum of weighted events). Sample dependent
        # for the correct pre-selection XS
        self.normalisation = {}

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

        sum_weights = (event.genWeight * event.WeightQCDEWK).sum()
        name_no_ext = event.config.dataset.name.split("_ext")[0]
        if name_no_ext in self.normalisation:
            self.normalisation[name_no_ext] += sum_weights
        else:
            self.normalisation[name_no_ext] = sum_weights

    def merge(self, other):
        self.histograms.merge(other.histograms)

        # Add normalisations
        for dataset in other.normalisation:
            if dataset not in self.normalisation:
                self.normalisation[dataset] = other.normalisation[dataset]
            else:
                self.normalisation[dataset] += other.normalisation[dataset]

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

        self.parallel = build_parallel(
            parallel_mode = 'sge',
            quiet = False,
        )

    def collect(self, dataset_readers_list):
        histograms, normalisations = None, None
        for dataset, readers in dataset_readers_list:
            # Get histograms
            if histograms is None:
                histograms = readers[0].histograms
            else:
                histograms.merge(readers[0].histograms)

            # Get normalisations
            norms = readers[0].normalisation
            if normalisations is None:
                normalisations = norms
            else:
                for dataset in norms:
                    if dataset not in normalisations:
                        normalisations[dataset] = norm[dataset]
                    else:
                        normalisations[dataset] += norms[dataset]

        # Apply normalisation
        for identifier, histogram in histograms:
            norm = normalisations[identifier[2].split("_ext")[0]]
            histogram["yields"] /= norm
            histogram["variance"] /= norm

        histograms.save(self.outdir)
        if self.plot:
            self.draw(histograms)
        return dataset_readers_list

    def draw(self, histograms):
        datasets = list(set(n[0] for n, h in histograms.histograms))

        dataset_cutflow_histnames = set((n[0], n[1], n[3]) for n, h in histograms.histograms)
        dataset_cutflow_histnames = sorted(
            sorted(
                sorted(
                    dataset_cutflow_histnames,
                    key = lambda x: x[2],
                ),
                key = lambda x: x[1],
            ),
            key = lambda x: x[0],
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

        # Submit to the batch
        self.parallel.map(dist_ratio, args)

        return histograms

    def reload(self, outdir):
        histograms = Histograms()
        histograms.reload(os.path.join(outdir, self.name))
        self.draw(histograms)
