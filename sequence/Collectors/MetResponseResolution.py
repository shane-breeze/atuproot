import os
import copy
import numpy as np
from scipy.special import wofz

from drawing.dist_ratio import dist_ratio
from drawing.dist_scatter_pull import dist_scatter_pull

# Take the cfg module and drop unpicklables
from Histogrammer import HistReader, HistCollector

class MetResponseResolutionReader(HistReader):
    def __init__(self, **kwargs):
        super(MetResponseResolutionReader, self).__init__(**kwargs)
        self.cfg.log = False

class MetResponseResolutionCollector(HistCollector):
    def __init__(self, **kwargs):
        super(MetResponseResolutionCollector, self).__init__(**kwargs)
        self.cfg.log = False

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
        args_response_resolution = []
        for dataset, cutflow, histname in dataset_cutflow_histnames:
            path = os.path.join(self.outdir, dataset, cutflow, "plots")
            if not os.path.exists(path):
                os.makedirs(path)

            hist_datas = None
            hists_mcs = []
            for n, h in histograms.histograms:
                if (n[0], n[1], n[3]) != (dataset, cutflow, histname):
                    continue

                if n[2] in datasets and dataset != n[2]:
                    continue

                if n[2] in ["MET", "SingleMuon", "SingleElectron"] and dataset != n[2]:
                    continue

                plot_items = [{
                    "name": n[3],
                    "category": h.histogram["bins"][1][icat],
                    "sample": n[2],
                    "bins": h.histogram["bins"][0],
                    "counts": h.histogram["counts"][:,icat],
                    "yields": h.histogram["yields"][:,icat],
                    "variance": h.histogram["variance"][:,icat],
                } for icat in range(h.histogram["counts"].shape[1])]

                if n[2] == dataset:
                    hist_datas = plot_items
                else:
                    hists_mcs.append(plot_items)

            if hist_datas is None or hists_mcs == []:
                continue

            # Perform Voigtian fits
            results = self.analyze(hist_datas, hists_mcs)

            for icat in range(len(hist_datas)):
                hist_data = hist_datas[icat]
                hist_data["function"] = results["data"][icat]["function"]
                if plot_items[icat]["category"] >= 250.:
                    hist_data = None
                hists_mc = [h[icat] for h in hists_mcs]
                for h in hists_mc:
                    h["function"] = results["mc"][icat]["function"]

                if icat < len(hist_datas)-1:
                    self.cfg.text = r'${:.0f} \leq E_{{T}}^{{miss}} < {:.0f}$ GeV'.format(
                        plot_items[icat]["category"],
                        plot_items[icat+1]["category"],
                    )
                else:
                    self.cfg.text = r'$E_{{T}}^{{miss}} \geq {:.0f}$ GeV'.format(
                        plot_items[icat]["category"],
                    )

                args.append([
                    hist_data,
                    hists_mc,
                    os.path.abspath(os.path.join(path, "{}_{}".format(histname, hists_mc[0]["category"]))),
                    copy.deepcopy(self.cfg),
                ])

            means = {
                "name": results["name"],
                "sample": results["sample"],
                "bins": results["bins"],
                "data": [r["mean"] for r in results["data"]],
                "mc": [r["mean"] for r in results["mc"]],
            }
            widths = {
                "name": results["name"],
                "sample": results["sample"],
                "bins": results["bins"],
                "data": [r["width"] for r in results["data"]],
                "mc": [r["width"] for r in results["mc"]],
            }

            args_response_resolution.extend([
                (means, os.path.abspath(os.path.join(path, "{}__response".format(histname))), self.cfg),
                (widths, os.path.abspath(os.path.join(path, "{}__resolution".format(histname))), self.cfg),
            ])

        self.parallel.parallel_mode = "multiprocessing"
        self.parallel.map(dist_ratio, args)
        self.parallel.map(dist_scatter_pull, args_response_resolution)

        return histograms

    def analyze(self, hist_datas, hists_mcs):
        results = []
        for icat in range(len(hist_datas)):
            hist_data = hist_datas[icat]
            hists_mc = [h[icat] for h in hists_mcs]
            total_mc = sum(h["yields"].sum() for h in hists_mc)

            hist_mc_sum = {
                "name": hists_mc[0]["name"],
                "sample": hists_mc[0]["sample"],
                "bins": hists_mc[0]["bins"],
                "counts": sum(h["counts"] for h in hists_mc if h["yields"].sum()>=0.01*total_mc),
                "yields": sum(h["yields"] for h in hists_mc if h["yields"].sum()>=0.01*total_mc),
                "variance": sum(h["variance"] for h in hists_mc if h["yields"].sum()>=0.01*total_mc),
            }

            data_results = self.fit(hist_data, errs="none")
            mc_results = self.fit(hist_mc_sum, errs="sumw2")

            results.append({
                "name": hist_mc_sum["name"],
                "sample": hist_mc_sum["sample"],
                "bin": hist_data["category"],
                "data": data_results,
                "mc": mc_results,
            })

        results = {
            "name": results[0]["name"],
            "sample": results[0]["sample"],
            "bins": np.array([r["bin"] for r in results]),
            "data": [r["data"] for r in results],
            "mc": [r["mc"] for r in results],
        }

        return results

    def fit(self, data, errs="none"):
        import ROOT

        bins = data["bins"][1:-1]
        yields = data["yields"][1:-1]
        vars = data["variance"][1:-1]

        hdata = ROOT.TH1D("data", "", len(bins)-1, bins)
        if errs == "sumw2": hdata.Sumw2()

        for ibin in range(1, hdata.GetNbinsX()+1):
            hdata.SetBinContent(ibin, yields[ibin-1])
            if errs == "sumw2":
                hdata.SetBinError(ibin, np.sqrt(vars[ibin-1]))

        x = ROOT.RooRealVar("x", "x", -250, 250)
        l = ROOT.RooArgList(x)
        data = ROOT.RooDataHist("data", "data", l, hdata)

        ws = ROOT.RooWorkspace("ws")
        getattr(ws, "import")(x)
        ws.factory("Voigtian:voig(x, mu[10,-100,100], gam[3,0.01,20], sig[25,0.01,100])")
        model = ws.pdf("voig")

        args = [ROOT.RooFit.Minimizer("Minuit", "Migrad"),
                ROOT.RooFit.Offset(True),
                ROOT.RooFit.PrintLevel(-1),
                ROOT.RooFit.Save()]
        if errs == "sumw2":
            args.append(ROOT.RooFit.SumW2Error(True))

        fit_result = model.fitTo(data, *args)

        from uncertainties import ufloat
        mu = ws.var("mu")
        mean = ufloat(mu.getValV(), mu.getError())

        sig = ws.var("sig")
        sigma = ufloat(sig.getValV(), sig.getError())

        gam = ws.var("gam")
        gamma = ufloat(gam.getValV(), gam.getError())

        # https://en.wikipedia.org/wiki/Voigt_profile
        width_breit = 2.*gamma
        width_gauss = 2.*sigma*(2.*np.log(2.)**0.5)
        phi = width_breit / width_gauss
        c0 = 2.0056
        c1 = 1.0593
        width = width_gauss * (1. - c0*c1 + (phi**2 + 2.*c1*phi + c0**2*c1**2)**0.5)

        def voigt(x, mean, sigma, gamma):
            z = ((x-mean) + 1j*gamma*0.5) / (sigma*np.sqrt(2))
            return np.real(wofz(z)) / (sigma*np.sqrt(2*np.pi))

        xs = (bins[1:] + bins[:-1])/2
        results = {
            "mean": (mean.n, mean.s),
            "sigma": (sigma.n, sigma.s),
            "gamma": (gamma.n, gamma.s),
            "width": (width.n, width.s),
            "function": (xs, voigt(xs, mean.n, sigma.n, gamma.n)),
        }
        return results
