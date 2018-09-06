from misc.cms_tdr_style import cms_tdr_style
#from misc.cms_header import cms_header
#from misc.set_hist_style import set_hist_style
#from misc.draw_line import draw_line
import numpy as np
import matplotlib.pyplot as plt

def taper_and_drop(hist):
    hist["counts"][-2] += hist["counts"][-1]
    hist["yields"][-2] += hist["yields"][-1]
    hist["variance"][-2] += hist["variance"][-1]

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
        "bins": hists_mc[0]["bins"],
        "counts": sum(h["counts"] for h in hists_mc),
        "yields": sum(h["yields"] for h in hists_mc),
        "variance": sum(h["variance"] for h in hists_mc),
    }
    hists_mc = sorted(hists_mc, key=lambda x: x["yields"].sum())

    axtop.hist(
        [h["yields"] for h in hists_mc],
        bins = hists_mc[0]["bins"],
        log = True,
        stacked = True,
        color = [cfg.sample_colours[h["sample"]]
                 if h["sample"] in cfg.sample_colours
                 else "blue"
                 for h in hists_mc],
        label = [cfg.sample_names[h["sample"]]
                 if h["sample"] in cfg.sample_names
                 else h["sample"]
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
            label = cfg.sample_names[hist_data["sample"]] \
                     if hist_data["sample"] in cfg.sample_names \
                     else hist_data["sample"],
        )
        axtop.set_xlim(bins[0], bins[-1])
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
    mc_sum = hist_mc_sum["yields"].sum()
    labels = ["{} {:.2f}".format(
                  cfg.sample_names[h["sample"]] \
                   if h["sample"] in cfg.sample_names \
                   else h["sample"],
                  h["yields"].sum()/mc_sum,
              )
              for h in hists_mc]
    if hist_data is not None:
        labels += ["{} {:.2f}".format(
                       cfg.sample_names[hist_data["sample"]] \
                        if hist_data["sample"] in cfg.sample_names \
                        else hist_data["sample"],
                       hist_data["yields"].sum()/mc_sum,
                   )]
    axtop.legend(handles[::-1], labels[::-1],
                 labelspacing = 0.1)

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
