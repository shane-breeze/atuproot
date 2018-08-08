import numpy as np
import os
import pickle

from . import Histogrammer_cfg as cfg
from datasets.datasets import get_datasets
from utils.Lambda import Lambda
from drawing.dist_ratio import dist_ratio

class HistReader(object):
    def __init__(self, **kwargs):
        self.histogrammer_cfgs = cfg.histogrammer_cfgs
        self.string_conv_func = {}

    def begin(self, event):
        """
        Create an attribute which will be a tuple of histograms. Attribute name
        is:
            {name}__{cutflow}__{variable}
        The tuple contains:
            (counts, yields, variance)
        """
        for histogrammer_cfg in self.histogrammer_cfgs:
            for cutflow in histogrammer_cfg["cutflows"]:
                setattr(self, "__".join([histogrammer_cfg["name"], cutflow]), None)

            # Create Lambda functions out of strings
            for variable in histogrammer_cfg["variables"]:
                if variable not in self.string_conv_func:
                    self.string_conv_func[variable] = Lambda(variable)

    def end(self):
        # Remove unpicklables / large (memory) objects
        self.string_conv_func = {}

    def event(self, event):
        for histogrammer_cfg in self.histogrammer_cfgs:
            for cutflow in histogrammer_cfg["cutflows"]:
                selection = getattr(event, "Cutflow_{}".format(cutflow))
                weights = event.Weight[selection]
                variables = [self.string_conv_func[variable](event)[selection]
                             for variable in histogrammer_cfg["variables"]]

                bins = histogrammer_cfg["bins"][0] if len(variables)==1 else histogrammer_cfg["bins"]
                varis = variables[0] if len(variables)==1 else variables
                weights1 = weights if len(variables)==1 else [weights]*len(variables)
                weights2 = weights**2 if len(variables)==1 else [weights**2]*len(variables)

                hist_counts, hist_bins = np.histogram(varis, bins=bins)
                hist_yields = np.histogram(varis,
                                           bins=bins,
                                           weights=weights1)[0]
                hist_variance = np.histogram(varis,
                                             bins=bins,
                                             weights=weights2)[0]

                name = "__".join([histogrammer_cfg["name"], cutflow])
                if getattr(self, name) is None:
                    setattr(self, name, (hist_bins, hist_counts, hist_yields, hist_variance))
                else:
                    other_bins, other_counts, other_yields, other_variance = getattr(self, name)
                    #assert hist_bins == other_bins
                    setattr(self, name, (hist_bins,
                                         other_counts + hist_counts,
                                         other_yields + hist_yields,
                                         other_variance + hist_variance))

    def merge(self, other):
        for histogrammer_cfg in self.histogrammer_cfgs:
            for cutflow in histogrammer_cfg["cutflows"]:
                name = "__".join([histogrammer_cfg["name"], cutflow])
                self_hists = getattr(self, name)
                other_hists = getattr(other, name)
                setattr(self, name,
                        tuple([self_hists[0]] +
                              map(sum, zip(self_hists[1:], other_hists[1:]))))

class HistCollector(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.outdir = "output"
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.datasets = get_datasets()

    def collect(self, dataset_readers_list):
        data = {}
        histname_cutflows = []
        for dataset, readers in dataset_readers_list:
            # get dataset
            dataset_object = next(d for d in self.datasets if d.name == dataset)

            for histogrammer_cfg in readers[0].histogrammer_cfgs:
                for cutflow in histogrammer_cfg["cutflows"]:
                    if (histogrammer_cfg["name"], cutflow) not in histname_cutflows:
                        histname_cutflows.append((histogrammer_cfg["name"], cutflow))
                    name = "__".join([histogrammer_cfg["name"], cutflow])
                    hist_bins, hist_counts, hist_yields, hist_variance = getattr(readers[0], name)

                    key = (dataset_object.parent, histogrammer_cfg["name"], cutflow)
                    if key in data:
                        other = data[key]
                        #assert other["bins"] == hist_bins

                        data[key] = {
                            "bins": hist_bins,
                            "counts": other["counts"]+hist_counts,
                            "yields": other["yields"]+hist_yields,
                            "variance": other["variance"]+hist_variance,
                        }
                    else:
                        data[key] = {
                            "bins": hist_bins,
                            "counts": hist_counts,
                            "yields": hist_yields,
                            "variance": hist_variance,
                        }

        for (parent, hist_name, cutflow), datum in data.items():
            outdir = os.path.join(self.outdir, cutflow, parent)
            if not os.path.exists(outdir):
                os.makedirs(outdir)

            path = os.path.join(outdir, hist_name+".pkl")
            with open(path, 'w') as f:
                pickle.dump(datum, f)

        self.draw(histname_cutflows, data)
        return dataset_readers_list

    def draw(self, histname_cutflows, data):
        for histname, cutflow in histname_cutflows:
            for dataset_name in ["MET", "SingleMuon", "SingleElectron"]:
                key = (dataset_name, histname, cutflow)
                if key not in data:
                    print "{} not in output".format(key)
                    continue
                hists_data = {dataset_name: data[key]}

                hist_data = {
                    "name": histname,
                    "sample": dataset_name,
                    "bins": data[key]["bins"],
                    "counts": data[key]["counts"],
                    "yields": data[key]["yields"],
                    "variance": data[key]["variance"],
                }

                try:
                    hists_mc = [{
                        "name": histname,
                        "sample": mc_dataset_name,
                        "bins": data[(mc_dataset_name, histname, cutflow)]["bins"],
                        "counts": data[(mc_dataset_name, histname, cutflow)]["counts"],
                        "yields": data[(mc_dataset_name, histname, cutflow)]["yields"],
                        "variance": data[(mc_dataset_name, histname, cutflow)]["variance"],
                    } for mc_dataset_name in ['DYJetsToLL', 'Diboson', 'EWKV2Jets',
                                              'G1Jet', 'QCD', 'SingleTop', 'TTJets',
                                              'VGamma', 'WJetsToLNu', 'ZJetsToNuNu']]
                except KeyError:
                    for mc_dataset_name in ['DYJetsToLL', 'Diboson', 'EWKV2Jets',
                                            'G1Jet', 'QCD', 'SingleTop', 'TTJets',
                                            'VGamma', 'WJetsToLNu', 'ZJetsToNuNu']:
                        key = (mc_dataset_name, histname, cutflow)
                        if key not in data:
                            print "{} not in output".format(key)
                    continue

                if not os.path.exists(os.path.join(self.outdir, cutflow, "plots")):
                    os.makedirs(os.path.join(self.outdir, cutflow, "plots"))

                dist_ratio(
                    hist_data,
                    hists_mc,
                    os.path.join(self.outdir, cutflow, "plots", dataset_name+"_"+histname+".pdf"),
                    cfg,
                )

    def reread(self, outdir):
        data = {}
        histname_cutflows = []
        for cutflow in os.listdir(outdir):
            for parent in os.listdir(os.path.join(outdir, cutflow)):
                if parent == "plots":
                    continue
                for hist_path in os.listdir(os.path.join(outdir, cutflow, parent)):
                    hist_name = os.path.splitext(os.path.basename(hist_path))[0]
                    if (hist_name, cutflow) not in histname_cutflows:
                        histname_cutflows.append((hist_name, cutflow))
                    with open(os.path.join(outdir, cutflow, parent, hist_path), 'r') as f:
                        data[(parent, hist_name, cutflow)] = pickle.load(f)
        self.draw(histname_cutflows, data)
        return data
