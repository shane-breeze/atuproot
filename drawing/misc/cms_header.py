import ROOT
from .draw_text import draw_text

def cms_header(header="Preliminary", en=13, lumi=35.9, size=0.045):
    try:
        tmarg = ROOT.gPad.GetPadTopMargin()-0.02
        lmarg = ROOT.gPad.GetPadLeftMargin()
        rmarg = ROOT.gPad.GetPadRightMargin()
    except AttributeError:
        tmarg = ROOT.gPad.GetTopMargin()-0.02
        lmarg = ROOT.gPad.GetLeftMargin()
        rmarg = ROOT.gPad.GetRightMargin()

    cms_text = "#bf{CMS} #it{"+header+"}"
    lumi_text = "{:.1f} fb^{{-1}} ({:.0f} TeV)".format(lumi, en)

    draw_text(cms_text, xpos=lmarg, ypos=1-tmarg, align=11, size=size)
    draw_text(lumi_text, xpos=1-rmarg, ypos=1-tmarg, align=31, size=size)
