import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import spline

def taper_and_drop(hist):
    """
    Final bin is an overflow.
    Remove underflow.
    """
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

def dist_ratio(hist_data, hists_mc, filepath, cfg):
    """
    Draw distributions with a ratio plot beneath.

    Parameters
    ----------

    hist_data : Dictionary holding the histogrammed information for the data
    {
        "name" : name of the distribution being plotted
        "sample" : name of the sample (presumable 'data' or similar)
        "bins" : numpy array of the bins edges used (size = (nbins+1,)). The
                 first bin is taken as the underflow and the last bin the
                 overflow
        "counts" : numpy array (size = (nbins,)) of the counts per bin (not
                   used for plotting yet)
        "yields" : numpy array (size = (nbins,)) of the yields per bin (what is
                  plotted)
        "variance" : numpy array (size = (nbins,)) of the variance per bin.
                     Sqrt of this is used for the error on the data. Symmetric
                     errors only so far.
        "function" : optional. numpy array (size = (nbins,)) for the y values
                     in each bin for a normalized (to 1) function to be
                     plotted (which will be smoothed)
    }
    hists_mc : List of dictionaries holding the histogrammed information for
               echo MC sample. Each dictionary is the same format as hist_data.
    filepath : str for the output file destination (without the extension)
    cfg : object with the following attributes:
        log : boolean. If True then the y-axis will be on a log-scale
        sample_colours : dict. Conversion between sample names and colours (for
                         MC samples only)
        sample_names : dict. Conversion between sample names and their labels
                       shown in the plot.
        axis_label : dict. Conversion between axis names and their labels shown
                     in the plot

    Returns
    -------
    "Success"
    """

    # Split axis into top and bottom with ratio 3:1
    # Share the x axis, not the y axis
    # Figure size is 4.8 by 6.4 inches
    fig, (axtop, axbot) = plt.subplots(
        nrows=2, ncols=1, sharex='col', sharey=False,
        gridspec_kw={'height_ratios': [3, 1]},
        figsize = (4.8, 6.4),
    )

    # Remove under/overflow bins (add overflow into final bin)
    hists_mc = [taper_and_drop(h) for h in hists_mc]
    if hist_data is not None:
        hist_data = taper_and_drop(hist_data)
        bins = hist_data["bins"]
    else:
        bins = hists_mc[0]["bins"]

    # MC sum histograms
    hist_mc_sum = {
        "name": hists_mc[0]["name"],
        "sample": hists_mc[0]["sample"],
        "bins": bins,
        "counts": sum(h["counts"] for h in hists_mc),
        "yields": sum(h["yields"] for h in hists_mc),
        "variance": sum(h["variance"] for h in hists_mc),
    }
    if "function" in hists_mc[0]:
        for key in hists_mc[0]:
            if key not in hist_mc_sum:
                hist_mc_sum[key] = hists_mc[0][key]

    # Total MC yield (integrated across the distribution)
    # Also sort MC histograms
    mc_sum = hist_mc_sum["yields"].sum()
    hists_mc = sorted(hists_mc, key=lambda x: x["yields"].sum())

    # Merge the smaller histograms into "Minors", except for QCD
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

    # Draw stacked MC
    axtop.hist(
        [h["yields"] for h in hists_mc],
        bins = bins,
        log = cfg.log,
        stacked = True,
        color = [cfg.sample_colours[h["sample"]]
                 if h["sample"] in cfg.sample_colours
                 else "blue"
                 for h in hists_mc],
        label = [h["sample"] for h in hists_mc],
    )

    # Draw MC total line
    axtop.hist(
        hist_mc_sum["yields"],
        bins = bins,
        log = cfg.log,
        histtype = 'step',
        color = "black",
    )

    if hist_data is not None:
        # Draw data error bars
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

        # Push x axis to bin limits (matplotlib normally adds padding)
        axtop.set_xlim(bins[0], bins[-1])

    # Draw functions if they exist
    title = []
    if hist_data is not None and "function" in hist_data:
        xs, ys = hist_data["function"]
        try:
            title.append(hist_data["text"])
        except TypeError:
            pass
        ys = mc_sum*ys / sum(ys)
        xnew = np.linspace(xs.min(), xs.max(), xs.shape[0]*4)
        ynew = spline(xs, ys, xnew)
        axtop.plot(xnew, ynew, color="k", ls='--', label="Data fit")

    if "function" in hist_mc_sum:
        xs, ys = hist_mc_sum["function"]
        try:
            title.append(hist_mc_sum["text"])
        except TypeError:
            pass
        ys = mc_sum*ys / sum(ys)
        xnew = np.linspace(xs.min(), xs.max(), xs.shape[0]*4)
        ynew = spline(xs, ys, xnew)
        axtop.plot(xnew, ynew, color="r", ls='--', label="MC fit")

    # Set ymin limit to maximum matplotlib's chosen minimum and 0.5
    ymin = max(axtop.get_ylim()[0], 0.5)
    axtop.set_ylim(ymin, None)

    # Add CMS text to top + energy + lumi
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

    # Legend - reverse the labels
    handles, labels = axtop.get_legend_handles_labels()
    handles = handles[::-1]
    labels = labels[::-1]

    # Add fraction of MC total to each legend label
    fractions = {
        h["sample"]: h["yields"].sum()/mc_sum
        for h in hists_mc
    }
    if hist_data is not None:
        fractions[hist_data["sample"]] = hist_data["yields"].sum()/mc_sum
    labels = ["{} {:.2f}".format(cfg.sample_names[label], fractions[label])
              if label in cfg.sample_names else label for label in labels]

    # Additional text added to the legend title
    if hasattr(cfg, "text"):
        title.append(cfg.text)
    axtop.legend(handles, labels, title="\n".join(title), labelspacing=0.1)

    if hist_data is not None:
        # Data / MC in the ratio
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

    # MC stat uncertainty in the ratio
    axbot.fill_between(
        bins,
        list(1. - (np.sqrt(hist_mc_sum["variance"]) / hist_mc_sum["yields"])) + [1.],
        list(1. + (np.sqrt(hist_mc_sum["variance"]) / hist_mc_sum["yields"])) + [1.],
        step = 'post',
        color = "#aaaaaa",
        label = "MC stat. unc.",
    )

    # Ratio legend
    handles, labels = axbot.get_legend_handles_labels()
    axbot.legend(handles, labels)

    # x and y limits for the ratio plot
    axbot.set_xlim(bins[0], bins[-1])
    axbot.set_ylim(0.5, 1.5)

    # x and y title labels for the ratio (axtop shares x-axis)
    name = hists_mc[0]["name"]
    name = name[0] if isinstance(name, list) else name
    axbot.set_xlabel(cfg.axis_label[name] if name in cfg.axis_label else name,
                     fontsize='large')
    axbot.set_ylabel("Data / SM Total",
                     fontsize='large')

    # Dashed line at 1. in the ratio plot
    axbot.plot(
        [bins[0], bins[-1]],
        [1., 1.],
        color = 'black',
        linestyle = ':',
    )

    # Report
    print("Creating {}".format(filepath))

    # Actually save the figure
    plt.tight_layout()
    fig.savefig(filepath+".pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)

    return "Success"
