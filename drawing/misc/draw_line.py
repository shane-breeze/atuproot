import ROOT

def draw_line(*pos, **kwargs):
    line = ROOT.TLine()
    line.SetLineStyle(7)
    if "ndc" in kwargs and kwargs["ndc"]:
        line.DrawLineNDC(*pos)
    else:
        line.DrawLine(*pos)
