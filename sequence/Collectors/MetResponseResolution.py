import os
import operator
import copy
import re
import numpy as np
from scipy.special import wofz

from drawing.dist_ratio import dist_ratio
from drawing.dist_scatter_pull import dist_scatter_pull

# Take the cfg module and drop unpicklables
from Histogrammer import HistReader, HistCollector

latex_eq_regex = re.compile("\$(.*)\$")

class MetResponseResolutionReader(HistReader):
    def __init__(self, **kwargs):
        super(MetResponseResolutionReader, self).__init__(**kwargs)
        self.cfg.log = False

class MetResponseResolutionCollector(HistCollector):
    def __init__(self, **kwargs):
        super(MetResponseResolutionCollector, self).__init__(**kwargs)
        self.cfg.log = False

    def draw(self, histograms):
        datasets = list(set(
            n[0] for n, _ in histograms.histograms
        ))

        # Set and sort to get all unique combinations of (dataset, cutflow, histname)
        dataset_cutflow_histnames = set(
            (n[0], n[1], tuple(n[3])) for n, _ in histograms.histograms
        )
        dataset_cutflow_histnames = sorted(
            dataset_cutflow_histnames, key=operator.itemgetter(2, 1, 0),
        )

        args = []
        args_response_resolution = []
        for dataset, cutflow, histnames in dataset_cutflow_histnames:
            path = os.path.join(self.outdir, dataset, cutflow)
            if not os.path.exists(path):
                os.makedirs(path)

            hist_datas = None
            hists_mcs = []
            for n, h in histograms.histograms:
                if (n[0], n[1], tuple(n[3])) != (dataset, cutflow, histnames):
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

                name = plot_items[icat]["name"][1]
                name = self.cfg.axis_label.get(name, name)
                if icat < len(hist_datas)-1:
                    self.cfg.text = r'${:.0f} \leq {} < {:.0f}$ GeV'.format(
                        plot_items[icat]["category"],
                        latex_eq_regex.search(name).group(1),
                        plot_items[icat+1]["category"],
                    )
                else:
                    self.cfg.text = r'${} \geq {:.0f}$ GeV'.format(
                        latex_eq_regex.search(name).group(1),
                        plot_items[icat]["category"],
                    )

                args.append([
                    hist_data,
                    hists_mc,
                    os.path.abspath(os.path.join(path, "{}_{}".format("_vs_".join(histnames), hists_mc[0]["category"]))),
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
                (means, os.path.abspath(os.path.join(path, "{}__response".format("_vs_".join(histnames)))), self.cfg),
                (widths, os.path.abspath(os.path.join(path, "{}__resolution".format("_vs_".join(histnames)))), self.cfg),
            ])

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

        x = ROOT.RooRealVar("x", "x", bins[0], bins[-1])
        l = ROOT.RooArgList(x)
        data = ROOT.RooDataHist("data", "data", l, hdata)

        mean_guess = hdata.GetMean()
        width_guess = hdata.GetStdDev()

        mu_eq = "mu[{},{},{}]".format(mean_guess, bins[0], bins[-1])
        gam_eq = "gam[{},{},{}]".format(width_guess, width_guess/20., width_guess*20.)
        sig_eq = "sig[{},{},{}]".format(width_guess, width_guess/20., width_guess*20.)
        voig_eq = "Voigtian:voig(x, {}, {}, {})".format(mu_eq, gam_eq, sig_eq)

        ws = ROOT.RooWorkspace("ws")
        getattr(ws, "import")(x)
        ws.factory(voig_eq)
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
