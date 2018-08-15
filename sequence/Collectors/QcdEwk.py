import os
from drawing.multi_dists import multi_dists

from .Histogrammer import HistCollector

class QcdEwkCollector(HistCollector):
    def draw(self, histograms):
        cutflow_histnames = list(set([(k[0], k[2].split("_Weight")[0]) for k in histograms]))
        parents = ["ZJetsToNuNu", "WJetsToLNu", "DYJetsToLL"]

        for cutflow, histname in cutflow_histnames:
            keys = [k
                    for weight in ["WeightNominal", "WeightEW"]
                    for k in histograms
                    if k[0] == cutflow and \
                    k[1] in parents and \
                    k[2] == histname + "_" + weight]

            hists = [{
                "name": key[2],
                "sample": key[1],
                "bins": histograms[key]["bins"],
                "counts": histograms[key]["counts"],
                "yields": histograms[key]["yields"],
                "variance": histograms[key]["variance"],
            } for key in keys]

            path = os.path.join(self.outdir, self.name, cutflow, "plots")
            if not os.path.exists(path):
                os.makedirs(path)

            multi_dists(
                hists,
                os.path.join(path, histname),
                self.cfg,
            )
