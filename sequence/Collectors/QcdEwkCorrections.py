import os
import numpy as np
import operator

from drawing.dist_comp import dist_comp
from Histogrammer import HistReader, HistCollector, Config

class QcdEwkCorrectionsReader(HistReader):
    def __init__(self, **kwargs):
        super(QcdEwkCorrectionsReader, self).__init__(**kwargs)
        self.split_samples = {}

class QcdEwkCorrectionsCollector(HistCollector):
    def draw(self, histograms):
        datasets = list(set(
            n[0] for n, _ in histograms.histograms
        ))

        # Set and sort to get all unique combinations of (dataset, cutflow, samples)
        dataset_cutflow_histnames = set(
            (n[0], n[1], n[3])
            for n, _ in histograms.histograms
            if "corrected" not in n[3]
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

            hist_pairs = {}
            for hname in (histname, histname+"_corrected"):
                for n, h in histograms.histograms:
                    if n[2] not in ["ZJetsToNuNu", "WJetsToLNu", "DYJetsToLL"]:
                        continue

                    if (n[0], n[1], n[3]) != (dataset, cutflow, hname):
                        continue

                    if n[2] in datasets and dataset != n[2]:
                        continue

                    if n[2] in ["MET", "SingleMuon", "SingleElectron"] and dataset != n[2]:
                        continue

                    if n[2] in hist_pairs:
                        hist_pairs[n[2]].append({
                            "name": n[3],
                            "sample": n[2],
                            "bins": h.histogram["bins"],
                            "counts": h.histogram["counts"],
                            "yields": h.histogram["yields"],
                            "variance": h.histogram["variance"],
                        })
                    else:
                        hist_pairs[n[2]] = [{
                            "name": n[3],
                            "sample": n[2],
                            "bins": h.histogram["bins"],
                            "counts": h.histogram["counts"],
                            "yields": h.histogram["yields"],
                            "variance": h.histogram["variance"],
                        }]
            args.append([hist_pairs.values(), filepath, self.cfg])
        return [(dist_comp, arg) for arg in args]
