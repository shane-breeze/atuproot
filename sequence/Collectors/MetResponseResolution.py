import ROOT
import os
import operator
import copy
import re
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 10000)

from scipy.special import wofz
from uncertainties import ufloat

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
        datasets = ["MET", "SingleMuon", "SingleElectron"]
        order = ["dataset", "region", "process", "yvariable", "xvariable",
                 "weight", "ybin_low", "ybin_upp", "xbin_low", "xbin_upp",
                 "count", "yield", "variance"]

        df_list = []
        for n, h in histograms.histograms:
            for icat in range(h.histogram["counts"].shape[1]-1):
                sub_df = pd.DataFrame({
                    "xbin_low": h.histogram["bins"][0][:-1],
                    "xbin_upp": h.histogram["bins"][0][1:],
                    "count": h.histogram["counts"][:,icat],
                    "yield": h.histogram["yields"][:,icat],
                    "variance": h.histogram["variance"][:,icat],
                })
                sub_df["dataset"] = n[0]
                sub_df["region"] = n[1]
                sub_df["process"] = n[2]
                sub_df["xvariable"] = n[3][0]
                sub_df["yvariable"] = n[3][1]
                sub_df["ybin_low"] = h.histogram["bins"][1][icat]
                sub_df["ybin_upp"] = h.histogram["bins"][1][icat+1]
                sub_df["weight"] = n[4]
                sub_df = sub_df[order]
                df_list.append(sub_df)
        df = pd.concat(df_list)
        for variation in self.variations:
            df["xvariable"] = df["xvariable"].apply(lambda x: x.replace(variation, ""))
            df["yvariable"] = df["yvariable"].apply(lambda y: y.replace(variation, ""))

        # Create mc sum
        df_mcsum = df[~df.process.isin(datasets)]\
                .groupby(["dataset", "region", "yvariable", "xvariable",
                          "weight", "ybin_low", "ybin_upp", "xbin_low",
                          "xbin_upp"])\
                .sum()\
                .reset_index()
        df_mcsum["process"] = "MCTotal"
        df = pd.concat([df, df_mcsum])[order]

        # Do the fitting
        df_fit = df[df.process.isin(datasets+["MCTotal"])]\
                 .groupby(["dataset", "region", "process", "yvariable",
                           "xvariable", "weight", "ybin_low", "ybin_upp"])\
                 .apply(fit)\
                 .reset_index()
        print(df_fit)
        exit()

        #datasets = list(set(
        #    n[0] for n, _ in histograms.histograms
        #))

        ## Set and sort to get all unique combinations of (dataset, cutflow, histname)
        #dataset_cutflow_histnames = set(
        #    (n[0], n[1], tuple(n[3]))
        #    for n, _ in histograms.histograms
        #    if not any(variation in n[1] for variation in self.variations)
        #)

        #dataset_cutflow_histnames = sorted(
        #    dataset_cutflow_histnames, key=operator.itemgetter(2, 1, 0),
        #)

        #args = []
        #args_response_resolution = []
        #for dataset, cutflow, histnames in dataset_cutflow_histnames:
        #    path = os.path.join(self.outdir, dataset, cutflow)
        #    if not os.path.exists(path):
        #        os.makedirs(path)

        #    hist_datas = None
        #    hists_mcs = []
        #    for variation in [""]+self.variations:
        #        for n, h in histograms.histograms:
        #            # Check dataset and cutflow match
        #            if (n[0], n[1]) != (dataset, cutflow+variation):
        #                continue

        #            # Check if histnames match (ignoring variation names)
        #            test = []
        #            for histname in n[3]:
        #                histname_novar = copy.deepcopy(histname)
        #                for variation in self.variations:
        #                    histname_novar = histname_novar.replace(variation, "")
        #                test.append(histname_novar)
        #            if tuple(test) != histnames:
        #                continue

        #            # If the process is in the datasets then the dataset and
        #            # process must match (i.e. it's data)
        #            if n[2] in datasets and dataset != n[2]:
        #                continue

        #            # Only do known datasets
        #            if n[2] in ["MET", "SingleMuon", "SingleElectron"] and dataset != n[2]:
        #                continue

        #            plot_items = [{
        #                "name": n[3],
        #                "category": h.histogram["bins"][1][icat],
        #                "sample": n[2],
        #                "bins": h.histogram["bins"][0],
        #                "counts": h.histogram["counts"][:,icat],
        #                "yields": h.histogram["yields"][:,icat],
        #                "variance": h.histogram["variance"][:,icat],
        #            } for icat in range(h.histogram["counts"].shape[1])]

        #            if n[2] == dataset:
        #                print(plot_items[0]["name"])
        #                print(plot_items[0]["sample"])
        #                hist_datas = plot_items
        #            else:
        #                hists_mcs.append(plot_items)
        #    exit()

        #    if hist_datas is None or hists_mcs == []:
        #        continue

        #    # # Perform Voigtian fits
        #    # results = self.analyze(hist_datas, hists_mcs)

        #    # for icat in range(len(hist_datas)):
        #    #     hist_data = hist_datas[icat]
        #    #     hist_data.update(results["data"][icat])
        #    #     #if plot_items[icat]["category"] >= 250.:
        #    #     #    hist_data = None
        #    #     hists_mc = [h[icat] for h in hists_mcs]
        #    #     for h in hists_mc:
        #    #         h.update(results["mc"][icat])

        #    #     name = plot_items[icat]["name"][1]
        #    #     name = self.cfg.axis_label.get(name, name)
        #    #     if icat < len(hist_datas)-1:
        #    #         self.cfg.text = r'${:.0f} \leq {} < {:.0f}$ GeV'.format(
        #    #             plot_items[icat]["category"],
        #    #             latex_eq_regex.search(name).group(1),
        #    #             plot_items[icat+1]["category"],
        #    #         )
        #    #     else:
        #    #         self.cfg.text = r'${} \geq {:.0f}$ GeV'.format(
        #    #             latex_eq_regex.search(name).group(1),
        #    #             plot_items[icat]["category"],
        #    #         )

        #    #     args.append([
        #    #         hist_data,
        #    #         hists_mc,
        #    #         os.path.abspath(os.path.join(path, "{}_{}".format("_vs_".join(histnames), hists_mc[0]["category"]))),
        #    #         copy.deepcopy(self.cfg),
        #    #     ])

        #    #means = {
        #    #    "name": results["name"],
        #    #    "sample": results["sample"],
        #    #    "bins": results["bins"],
        #    #    "data": [r["mean"] for r in results["data"]],
        #    #    "mc": [r["mean"] for r in results["mc"]],
        #    #}
        #    #widths = {
        #    #    "name": results["name"],
        #    #    "sample": results["sample"],
        #    #    "bins": results["bins"],
        #    #    "data": [r["width"] for r in results["data"]],
        #    #    "mc": [r["width"] for r in results["mc"]],
        #    #}

        #    #args_response_resolution.extend([
        #    #    (means, os.path.abspath(os.path.join(path, "{}__response".format("_vs_".join(histnames)))), self.cfg),
        #    #    (widths, os.path.abspath(os.path.join(path, "{}__resolution".format("_vs_".join(histnames)))), self.cfg),
        #    #])
        #exit()
        return []
        #return [(dist_ratio, arg) for arg in args]\
        #        + [(dist_scatter_pull, arg) for arg in args_response_resolution]

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
            if "text" in data_results:
                data_results["text"] = ["Data:"] + data_results["text"]
            if "text" in mc_results:
                mc_results["text"] = ["MC:"] + mc_results["text"]

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

        if yields.sum() == 0.:
            return {
                "mean": (0., 0.),
                "sigma": (0., 0.),
                "gamma": (0., 0.),
                "width": (0., 0.),
            }

        hdata = ROOT.TH1D("data", "", len(bins)-1, bins)
        if errs == "sumw2": hdata.Sumw2()

        for ibin in range(1, hdata.GetNbinsX()+1):
            hdata.SetBinContent(ibin, yields[ibin-1])
            if errs == "sumw2":
                hdata.SetBinError(ibin, np.sqrt(vars[ibin-1]))

        x = ROOT.RooRealVar("x", "x", bins[0], bins[-1])
        #xframe = x.frame()
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
        #data.plotOn(xframe)
        #model.plotOn(xframe)
        #chi2 = xframe.chiSquare(3)
        chi2 = 0.

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
        if width_gauss != 0.:
            phi = width_breit / width_gauss
            c0 = 2.0056
            c1 = 1.0593
            width = sigma * (1. - c0*c1 + (phi**2 + 2.*c1*phi + c0**2*c1**2)**0.5)
        else:
            width = width_breit
        # FWHM / (2*sqrt(2*ln(2)))

        def voigt(x, mean, sigma, gamma):
            z = ((x-mean) + 1j*gamma*0.5) / (sigma*np.sqrt(2))
            return np.real(wofz(z)) / (sigma*np.sqrt(2*np.pi))

        def get_sfs(val):
            n = 0
            test_val = copy.deepcopy(val)
            while test_val < 1.:
                test_val *= 10.
                n += 1
            return n
        mean_fmt = "{:."+str(get_sfs(mean.s))+"f}"
        sigma_fmt = "{:."+str(get_sfs(width.s))+"f}"

        xs = (bins[1:] + bins[:-1])/2
        return {
            "mean": (mean.n, mean.s),
            "sigma": (sigma.n, sigma.s),
            "gamma": (gamma.n, gamma.s),
            "width": (width.n, width.s),
            "function": (xs, voigt(xs, mean.n, sigma.n, gamma.n)),
            "chi2": chi2,
            "ndof": len(bins)-3,
            "text": [
                (r'$\mu = '+mean_fmt+' \pm '+mean_fmt+'$').format(mean.n, mean.s),
                (r'$\sigma = '+sigma_fmt+' \pm '+sigma_fmt+'$').format(width.n, width.s),
            ],
        }

def fit(df):
    bins = df[["xbin_low"]].values[1:]
    yields = df[["yield"]].values[1:-1]
    vars = df[["variance"]].values[1:-1]

    if yields.sum() == 0.:
        return pd.DataFrame({
            "mean": [0.],
            "mean_unc": [0.],
            "sigma": [0.],
            "sigma_unc": [0.],
            "width": [0.],
            "width_unc": [0.],
        })

    hdata = ROOT.TH1D("data", "", len(bins)-1, bins)

    errs = np.array_equal(yields, vars)
    if errs: hdata.Sumw2()

    for ibin in range(1, hdata.GetNbinsX()+1):
        hdata.SetBinContent(ibin, yields[ibin-1])
        hdata.SetBinError(ibin, np.sqrt(vars[ibin-1]))

    x = ROOT.RooRealVar("x", "x", bins[0], bins[-1])
    #xframe = x.frame()
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
    if errs:
        args.append(ROOT.RooFit.SumW2Error(True))

    fit_result = model.fitTo(data, *args)
    #data.plotOn(xframe)
    #model.plotOn(xframe)
    #chi2 = xframe.chiSquare(3)
    chi2 = 0.

    mu = ws.var("mu")
    mean = ufloat(mu.getValV(), mu.getError())

    sig = ws.var("sig")
    sigma = ufloat(sig.getValV(), sig.getError())

    gam = ws.var("gam")
    gamma = ufloat(gam.getValV(), gam.getError())

    # https://en.wikipedia.org/wiki/Voigt_profile
    # FWHM / (2*sqrt(2*ln(2)))
    width_breit = 2.*gamma
    width_gauss = 2.*sigma*(2.*np.log(2.)**0.5)
    if width_gauss != 0.:
        phi = width_breit / width_gauss
        c0 = 2.0056
        c1 = 1.0593
        width = sigma * (1. - c0*c1 + (phi**2 + 2.*c1*phi + c0**2*c1**2)**0.5)
    else:
        width = width_breit

    return pd.DataFrame({
        "mean": [mean.n],
        "mean_unc": [mean.s],
        "sigma": [sigma.n],
        "sigma_unc": [sigma.s],
        "gamma": [gamma.n],
        "gamma_unc": [gamma.s],
        "width": [width.n],
        "width_unc": [width.s],
        "chi2": [chi2],
        "ndof": [len(bins)-3],
    })

def voigt(x, mean, sigma, gamma):
    z = ((x-mean) + 1j*gamma*0.5) / (sigma*np.sqrt(2))
    return np.real(wofz(z)) / (sigma*np.sqrt(2*np.pi))

