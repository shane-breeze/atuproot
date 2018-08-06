from misc.cms_tdr_style import cms_tdr_style
from misc.cms_header import cms_header
from misc.set_hist_style import set_hist_style
from collections import namedtuple
import numpy as np

from rootpy.plotting import Canvas, Legend, Hist, HistStack
from rootpy.plotting.utils import draw

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
    return new_hist

def dist_ratio(hist_data_cfg, hists_mc_cfg, filepath):
    cms_tdr_style()

    hist_data = Histogram(**hist_data_cfg)
    hists_mc = [Histogram(**hist_mc_cfg) for hist_mc_cfg in hists_mc_cfg]

    hists_mc_sum = Histogram(name = hists_mc[0].name,
                             bins = hists_mc[0].bins,
                             counts = sum([hist_mc.counts for hist_mc in hists_mc]),
                             yields = sum([hist_mc.yields for hist_mc in hists_mc]),
                             variance = sum([hist_mc.variance for hist_mc in hists_mc]))

    hist_data.hist = convert_to_hist(hist_data)
    set_hist_style(hist_data.hist, kind="data")
    for hist_mc in hists_mc:
        hist_mc.hist = convert_to_hist(hist_mc)
        set_hist_style(hist_mc.hist, kind="mc")
    hists_mc_sum.hist = convert_to_hist(hists_mc_sum)
    set_hist_style(hists_mc_sum.hist, kind="mc")

    stack_mc = HistStack([h.hist for h in hists_mc])

    canvas = Canvas(height=750, width=650)
    axes, ranges = draw(
        [hists_mc_sum.hist, stack_mc, hist_data.hist],
        logy = True,
    )
    canvas.save_as(filepath)

if __name__ == "__main__":
    h = Hist([0,1,2])
    print dir(h)
