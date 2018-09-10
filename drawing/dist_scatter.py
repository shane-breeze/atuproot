import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle

def make_error_boxes(ax, xdata, ydata, xerror, yerror, facecolor='r',
                     edgecolor='r', alpha=1.0):
    errorboxes = [
        Rectangle((x-xe, y-ye), 2*xe, 2*ye,
                  fc = facecolor,
                  ec = edgecolor,
                  alpha = alpha)
        for x, y, xe, ye in zip(xdata, ydata, xerror, yerror)
    ]

    pc = PatchCollection(errorboxes,
                         facecolor = facecolor,
                         edgecolor = edgecolor,
                         alpha = alpha)
    ax.add_collection(pc)
    return errorboxes[0]

def dist_scatter((results, filepath, cfg)):
    fig, (axtop, axbot) = plt.subplots(
        nrows=2, ncols=1, sharex='col', sharey=False,
        gridspec_kw={'height_ratios': [3, 1]},
        figsize = (4.8, 6.4),
    )
    axtop.set_xscale('log')

    bins = list(results["bins"][1:])
    bins = np.array(bins+[2*bins[-1]-bins[-2]])
    data_yields = np.array([r[0] for r in results["data"]][1:])
    data_errors = np.array([r[1] for r in results["data"]][1:])
    mc_yields = np.array([r[0] for r in results["mc"]][1:])
    mc_errors = np.array([r[1] for r in results["mc"]][1:])

    # top axes
    axtop.text(0, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
            ha='left', va='bottom', transform=axtop.transAxes,
            fontsize='large')

    axtop.text(1, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
            ha='right', va='bottom', transform=axtop.transAxes,
            fontsize='large')

    axtop.errorbar(
        (bins[1:] + bins[:-1])/2, data_yields,
        xerr=(bins[1:] - bins[:-1])/2, yerr=data_errors,
        fmt='o', markersize=3, linewidth=1,
        capsize=1.8, color="black", label="Data",
    )

    rect_eg = make_error_boxes(
        axtop,
        (bins[1:] + bins[:-1])/2, mc_yields,
        (bins[1:] - bins[:-1])/2, mc_errors,
        facecolor="#80b1d3",
        edgecolor="#5a9ac6",
    )

    handles, labels = axtop.get_legend_handles_labels()
    handles += [rect_eg]
    labels += ["MC"]
    axtop.legend(handles, labels)

    variable = (
        cfg.axis_label[results["name"]]
        if results["name"] in cfg.axis_label
        else results["name"]
    ).replace("(GeV)","").replace("$","")

    if filepath.endswith("response"):
        ylabel = r'$\mu({})$ (GeV)'.format(variable)
    elif filepath.endswith("resolution"):
        ylabel = r'$\sigma({})$ (GeV)'.format(variable)
    else:
        ylabel = r'${}$ (GeV)'.format(variable)

    axtop.set_ylabel(ylabel, fontsize = 'large')

    # bottom axes
    pull = (data_yields - mc_yields) / np.sqrt(data_errors**2 + mc_errors**2)
    axbot.plot((bins[1:] + bins[:-1])/2, pull,
               'o', ms=3, mfc='black', mec='black')
    axbot.set_xlabel(r'$E_{T}^{miss}$ (GeV)', fontsize='large')
    axbot.set_ylabel("Pull", fontsize='large')

    ylim = max(map(abs, axbot.get_ylim()))
    axbot.set_ylim(-ylim, ylim)
    axbot.axhline(-1, ls='--', color='grey', lw=1)
    axbot.axhline(1, ls='--', color='grey', lw=1)

    print("Creating {}".format(filepath))
    plt.tight_layout()
    fig.savefig(filepath+".pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)
