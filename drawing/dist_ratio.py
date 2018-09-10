from misc.cms_tdr_style import cms_tdr_style
#from misc.cms_header import cms_header
#from misc.set_hist_style import set_hist_style
#from misc.draw_line import draw_line
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import spline

def taper_and_drop(hist):
    hist["counts"][-2] += hist["counts"][-1]
    hist["yields"][-2] += hist["yields"][-1]
    hist["variance"][-2] += hist["variance"][-1]

    if isinstance(hist["bins"], list):
        hist["bins"] = hist["bins"][0]
    hist["bins"] = hist["bins"][1:-1]
    hist["counts"] = hist["counts"][1:-1]
    hist["yields"] = hist["yields"][1:-1]
    hist["variance"] = hist["variance"][1:-1]

    return hist

def dist_ratio((hist_data, hists_mc, filepath, cfg)):
    #cms_tdr_style()
    fig, (axtop, axbot) = plt.subplots(
        nrows=2, ncols=1, sharex='col', sharey=False,
        gridspec_kw={'height_ratios': [3, 1]},
        figsize = (4.8, 6.4),
    )

    hists_mc = [taper_and_drop(h) for h in hists_mc]
    if hist_data is not None:
        hist_data = taper_and_drop(hist_data)
        bins = hist_data["bins"]
    else:
        bins = hists_mc[0]["bins"]

    hist_mc_sum = {
        "name": hists_mc[0]["name"],
        "sample": hists_mc[0]["sample"],
        "bins": bins,
        "counts": sum(h["counts"] for h in hists_mc),
        "yields": sum(h["yields"] for h in hists_mc),
        "variance": sum(h["variance"] for h in hists_mc),
    }
    if "function" in hists_mc[0]:
        hist_mc_sum["function"] = hists_mc[0]["function"]
    mc_sum = hist_mc_sum["yields"].sum()
    hists_mc = sorted(hists_mc, key=lambda x: x["yields"].sum())

    # merge small
    hists_mc_lower_oneperc = [h
        for h in hists_mc
        if h["yields"].sum()/hist_mc_sum["yields"].sum() < 0.01 and h["sample"] != "QCD"
    ]
    hist_mc_minor = {
        "name": hists_mc[0]["name"],
        "sample": "Minor",
        "bins": bins,
        "counts": sum(h["counts"] for h in hists_mc_lower_oneperc),
        "yields": sum(h["yields"] for h in hists_mc_lower_oneperc),
        "variance": sum(h["variance"] for h in hists_mc_lower_oneperc),
    }
    new_hists_mc = [h
        for h in hists_mc
        if h["yields"].sum()/hist_mc_sum["yields"].sum() >= 0.01 or h["sample"] == "QCD"
    ]
    if not isinstance(hist_mc_minor["counts"], int):
        hists_mc = [hist_mc_minor]
    hists_mc += new_hists_mc[:]

    axtop.hist(
        [h["yields"] for h in hists_mc],
        bins = bins,
        log = cfg.log,
        stacked = True,
        color = [cfg.sample_colours[h["sample"]]
                 if h["sample"] in cfg.sample_colours
                 else "blue"
                 for h in hists_mc],
        label = [h["sample"]
                 for h in hists_mc],
    )

    if hist_data is not None:
        axtop.errorbar(
            (bins[1:] + bins[:-1])/2,
            hist_data["yields"],
            yerr = np.sqrt(hist_data["variance"]),
            fmt = 'o',
            markersize = 3,
            linewidth = 1,
            capsize = 1.8,
            color = cfg.sample_colours[hist_data["sample"]] \
                    if hist_data["sample"] in cfg.sample_colours \
                    else "black",
            label = hist_data["sample"],
        )
        axtop.set_xlim(bins[0], bins[-1])

    if hist_data is not None and "function" in hist_data:
        xs, ys = hist_data["function"]
        ys = mc_sum*ys / sum(ys)
        xnew = np.linspace(xs.min(), xs.max(), xs.shape[0]*4)
        ynew = spline(xs, ys, xnew)
        axtop.plot(xnew, ynew, color="k", ls='--', label="Data fit")

    if "function" in hist_mc_sum:
        xs, ys = hist_mc_sum["function"]
        ys = mc_sum*ys / sum(ys)
        xnew = np.linspace(xs.min(), xs.max(), xs.shape[0]*4)
        ynew = spline(xs, ys, xnew)
        axtop.plot(xnew, ynew, color="r", ls='--', label="MC fit")

    ymin = max(axtop.get_ylim()[0], 0.5)
    axtop.set_ylim(ymin, None)

    axtop.text(0, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
               horizontalalignment='left',
               verticalalignment='bottom',
               transform=axtop.transAxes,
               fontsize='large')

    axtop.text(1, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
               horizontalalignment='right',
               verticalalignment='bottom',
               transform=axtop.transAxes,
               fontsize='large')

    handles, labels = axtop.get_legend_handles_labels()
    handles = handles[::-1]
    labels = labels[::-1]

    fractions = {
        h["sample"]: h["yields"].sum()/mc_sum
        for h in hists_mc
    }
    if hist_data is not None:
        fractions[hist_data["sample"]] = hist_data["yields"].sum()/mc_sum

    labels = ["{} {:.2f}".format(cfg.sample_names[label], fractions[label])
              if label in cfg.sample_names else label for label in labels]

    if not hasattr(cfg, "text"):
        axtop.legend(handles, labels, labelspacing=0.1)
    else:
        axtop.legend(handles, labels, title=cfg.text, labelspacing=0.1)

    if hist_data is not None:
        axbot.errorbar(
            (bins[1:] + bins[:-1])/2,
            hist_data["yields"] / hist_mc_sum["yields"],
            yerr = np.sqrt(hist_data["variance"]) / hist_mc_sum["yields"],
            fmt = 'o',
            markersize = 3,
            linewidth = 1,
            capsize = 1.8,
            color = 'black',
        )

    axbot.fill_between(
        bins,
        list(1. - (np.sqrt(hist_mc_sum["variance"]) / hist_mc_sum["yields"])) + [1.],
        list(1. + (np.sqrt(hist_mc_sum["variance"]) / hist_mc_sum["yields"])) + [1.],
        step = 'post',
        color = "#aaaaaa",
        label = "MC stat. unc.",
    )

    handles, labels = axbot.get_legend_handles_labels()
    axbot.legend(handles, labels)

    axbot.set_xlim(bins[0], bins[-1])
    axbot.set_ylim(0.5, 1.5)

    axbot.set_xlabel(cfg.axis_label[hists_mc[0]["name"]]
                     if hists_mc[0]["name"] in cfg.axis_label
                     else hists_mc[0]["name"],
                     fontsize='large')
    axbot.set_ylabel("Data / SM Total",
                     fontsize='large')

    axbot.plot(
        [bins[0], bins[-1]],
        [1., 1.],
        color = 'black',
        linestyle = ':',
    )

    print("Creating {}".format(filepath))

    plt.tight_layout()
    fig.savefig(filepath+".pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)
