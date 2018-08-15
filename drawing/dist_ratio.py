from misc.cms_tdr_style import cms_tdr_style
from misc.cms_header import cms_header
from misc.set_hist_style import set_hist_style
from misc.draw_line import draw_line
import numpy as np
from random import getrandbits

try:
    from rootpy.plotting import Canvas, Pad, Legend, Hist, HistStack
    from rootpy.plotting.utils import draw
    has_rootpy = True
except ImportError:
    has_rootpy = False

class Histogram(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def convert_to_hist(histogram):
    bins = histogram.bins[1:-1]
    new_hist = Hist(bins)
    new_hist.Sumw2(True)
    for idx in range(len(new_hist)):
        new_hist[idx].value = histogram.yields[idx]
        new_hist[idx].error = np.sqrt(histogram.variance[idx])

    new_hist[-2].value += new_hist[-1].value
    new_hist[-2].error = np.sqrt(new_hist[-2].error**2 + new_hist[-1].error**2)

    return new_hist

def dist_ratio(hist_data_cfg, hists_mc_cfg, filepath, cfg):
    if not has_rootpy:
        return
    cms_tdr_style()

    hist_data = Histogram(**hist_data_cfg)
    hists_mc = [Histogram(**hist_mc_cfg) for hist_mc_cfg in hists_mc_cfg]

    hists_mc_sum = Histogram(name = hists_mc[0].name,
                             sample = hists_mc[0].sample,
                             bins = hists_mc[0].bins,
                             counts = sum([hist_mc.counts
                                           for hist_mc in hists_mc]),
                             yields = sum([hist_mc.yields
                                           for hist_mc in hists_mc]),
                             variance = sum([hist_mc.variance
                                             for hist_mc in hists_mc]))

    hist_data.hist = convert_to_hist(hist_data)
    set_hist_style(hist_data.hist, kind="data")
    hist_data.hist.linecolor = "black"
    hist_data.hist.markercolor = "black"
    for hist_mc in hists_mc:
        hist_mc.hist = convert_to_hist(hist_mc)
        set_hist_style(hist_mc.hist, kind="mc")
        hist_mc.hist.linecolor = cfg.sample_colours[hist_mc.sample] if hist_mc.sample in cfg.sample_colours else "black"
        hist_mc.hist.fillcolor = cfg.sample_colours[hist_mc.sample] if hist_mc.sample in cfg.sample_colours else "black"
        hist_mc.hist.fillstyle = 1001
    hists_mc_sum.hist = convert_to_hist(hists_mc_sum)
    set_hist_style(hists_mc_sum.hist, kind="mc")
    hists_mc_sum.hist.linecolor = "black"
    hists_mc_sum.hist.markercolor = "black"

    hists_mc = sorted(hists_mc, key=lambda x: x.hist.integral(overflow=True))
    stack_mc = HistStack([h.hist for h in hists_mc], drawstyle='hist')

    try:
        data_mini = min([hbin.value
                         for hbin in hist_data.hist
                         if hbin.value>0.])
        data_maxi = max([hbin.value
                         for hbin in hist_data.hist
                         if hbin.value>0.])
    except ValueError:
        data_mini, data_maxi = 1., 100.
    try:
        mc_sum_mini = min([hbin.value
                           for hbin in hists_mc_sum.hist
                           if hbin.value>0.])
        mc_sum_maxi = max([hbin.value
                           for hbin in hists_mc_sum.hist
                           if hbin.value>0.])
    except ValueError:
        mc_sum_mini, mc_sum_maxi = 1., 100.

    try:
        mc_sep_mini = min([hbin.value
                           for hbin in hists_mc[0].hist
                           if hbin.value>0.])
    except ValueError:
        mc_sep_mini = data_mini

    mini = max(min(mc_sum_mini, data_mini, mc_sep_mini), 0.5)
    maxi = max(mc_sum_maxi, data_maxi)

    # legend boundary

    new_ymin = pow(10, 1.1*np.log10(mini) - 0.1*np.log10(maxi))
    new_ymax = pow(10, 1.1*np.log10(maxi) - 0.1*np.log10(mini))

    canvas = Canvas(height=750, width=650)
    padtop = Pad(0., 0.3, 1.0, 1.0)
    padbot = Pad(0., 0., 1.0, 0.3)

    canvas.margin = 0.12, 0.06, 0.35, 0.1
    padtop.margin = 0.12, 0.06, 0.01, 0.1
    padbot.margin = 0.12, 0.06, 0.35, 0.01

    canvas.cd()
    padtop.Draw()
    padbot.Draw()

    xaxis, yaxis = hist_data.hist.xaxis, hist_data.hist.yaxis
    xaxis.set_tick_length(0.03*10./7.)
    xaxis.set_label_size(0.030*10./7.)
    xaxis.set_title_size(0.035*10./7.)
    yaxis.set_label_size(0.030*10./7.)
    yaxis.set_title_size(0.035*10./7.)

    (xaxis, yaxis), ranges = draw(
        [hist_data.hist, stack_mc, hists_mc_sum.hist, hist_data.hist],
        pad = padtop,
        ylimits = (new_ymin, new_ymax),
        logy = True,
        ytitle = "",
    )

    ratio = hist_data.hist.clone("rand{:0x}".format(getrandbits(6*4)))
    ratio.set_directory(None)

    for idx in range(len(ratio)):
        try:
            ratio[idx].value = hist_data.hist[idx].value / \
                               hists_mc_sum.hist[idx].value
            ratio[idx].error = hist_data.hist[idx].error / \
                               hists_mc_sum.hist[idx].value
        except ZeroDivisionError:
            ratio[idx].value = 0.
            ratio[idx].error = 0.

    xaxis, yaxis = ratio.xaxis, ratio.yaxis
    xaxis.set_tick_length(0.03*10./7.)
    xaxis.set_label_size(0.030*10./3.)
    xaxis.set_title_size(0.035*10./3.)
    xaxis.set_title_offset(1.2)
    yaxis.set_label_size(0.030*10./3.)
    yaxis.set_title_size(0.035*10./3.)
    yaxis.set_title_offset(0.5)

    (xaxis, yaxis), ranges = draw(
        [ratio],
        pad = padbot,
        ylimits = (0.45, 1.55),
        xtitle = cfg.axis_label[hist_data.name] if hist_data.name in cfg.axis_label else hist_data.name,
        ytitle = "Data / SM total",
    )

    padbot.cd()
    draw_line(ranges[0], 1., ranges[1], 1.)

    padtop.cd()
    cms_header(size=0.035*10./7.)

    canvas.save_as(filepath + ".pdf")
    #canvas.save_as(filepath + ".png")

    padtop.close()
    padbot.close()
    canvas.close()
