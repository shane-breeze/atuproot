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

def dist_comp(hist_pairs, filepath, cfg):
    """
    Draw distributions with a ratio plot beneath.

    Parameters
    ----------

    hist_pairs : List of pairs of dicts (ratio of the pairs shown in subplot).
                 Dicts have the following form:
    {
        "name" : name of the distribution being plotted
        "sample" : name of the sample (used for labelling)
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
    filepath : str for the output file destination (without the extension)
    cfg : object with the following attributes:
        log : boolean. If True then the y-axis will be on a log-scale
        sample_colours : dict. Conversion between sample names and colours
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
    hist_pairs = [map(taper_and_drop, hs) for hs in hist_pairs]
    bins = hist_pairs[0][0]["bins"]

    # Draw hists
    axtop.hist(
        [hs[0]["yields"] for hs in hist_pairs],
        bins = bins,
        log = cfg.log,
        histtype = 'step',
        color = [cfg.sample_colours.get(hs[0]["sample"], "blue")
                 for hs in hist_pairs],
        label = [cfg.sample_names.get(hs[0]["sample"], hs[0]["sample"])
                 for hs in hist_pairs],
        ls = '--',
    )
    axtop.hist(
        [hs[1]["yields"] for hs in hist_pairs],
        bins = bins,
        log = cfg.log,
        histtype = 'step',
        color = [cfg.sample_colours.get(hs[1]["sample"], "blue")
                 for hs in hist_pairs],
        label = [cfg.sample_names.get(hs[1]["sample"], hs[1]["sample"])+" (nNLO EW)"
                 for hs in hist_pairs],
    )
    axtop.set_xlim(bins[0], bins[-1])

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

    # Additional text added to the legend title
    if not hasattr(cfg, "text"):
        axtop.legend(handles, labels, labelspacing=0.1)
    else:
        axtop.legend(handles, labels, title=cfg.text, labelspacing=0.1)

    ratios = [{
        "name": hs[0]["name"],
        "sample": hs[0]["sample"],
        "bins": bins,
        "counts": hs[1]["counts"] + hs[0]["counts"],
        "yields": hs[1]["yields"] / hs[0]["yields"],
        "variance": (hs[1]["yields"]/hs[0]["yields"])**2*(hs[0]["variance"]/hs[0]["yields"]**2 + hs[1]["variance"]/hs[1]["yields"]**2),
    } for hs in hist_pairs]

    axbot.hist(
        [r["yields"] for r in ratios],
        bins = bins,
        histtype = 'step',
        color = [cfg.sample_colours.get(r["sample"], "blue") for r in ratios],
    )

    # x and y limits for the ratio plot
    axbot.set_xlim(bins[0], bins[-1])
    axbot.set_ylim(0.5, 1.5)

    # x and y title labels for the ratio (axtop shares x-axis)
    name = ratios[0]["name"]
    axbot.set_xlabel(cfg.axis_label[name] if name in cfg.axis_label else name,
                     fontsize='large')
    axbot.set_ylabel(r'$1+\kappa_{nNLO EW}$', fontsize='large')

    # Dashed line at 1. in the ratio plot
    axbot.plot([bins[0], bins[-1]], [1., 1.], color='black', linestyle=':')

    # Report
    print("Creating {}".format(filepath))

    # Actually save the figure
    plt.tight_layout()
    fig.savefig(filepath+".pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)

    return "Success"
