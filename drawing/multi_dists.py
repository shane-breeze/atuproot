from misc.cms_tdr_style import cms_tdr_style
from misc.cms_header import cms_header
from misc.set_hist_style import set_hist_style
import numpy as np

try:
    from rootpy.plotting import Canvas, Legend, Hist
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

def multi_dists(hist_cfgs, filepath, cfg):
    if not has_rootpy:
        return
    cms_tdr_style()

    hists = [Histogram(**hist_cfg) for hist_cfg in hist_cfgs]

    for hist in hists:
        hist.hist = convert_to_hist(hist)
        set_hist_style(hist.hist, kind="mc")
        hist.hist.linecolor = cfg.sample_colours[hist.sample]

    # legend boundary

    canvas = Canvas(height=700, width=700)
    canvas.margin = 0.1, 0.1, 0.1, 0.1

    xaxis, yaxis = hists[0].hist.xaxis, hists[0].hist.yaxis
    xaxis.set_tick_length(0.03)
    xaxis.set_label_size(0.030)
    xaxis.set_title_size(0.035)
    yaxis.set_label_size(0.030)
    yaxis.set_title_size(0.035)

    (xaxis, yaxis), ranges = draw(
        [h.hist for h in hists],
        pad = canvas,
        logy = True,
        ytitle = "",
    )

    cms_header(size=0.035*10./7.)

    canvas.save_as(filepath + ".pdf")
    #canvas.save_as(filepath + ".png")
    canvas.close()
