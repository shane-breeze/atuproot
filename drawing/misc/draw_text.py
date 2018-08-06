import ROOT

def draw_text(text, xpos=0.15, ypos=0.8,  font=42, size=0.045, align=12, ndc=True):
    label = ROOT.TLatex()
    label.SetTextColor()
    label.SetTextFont(font)
    label.SetTextSize(size)
    label.SetTextAlign(align)
    if ndc:
        label.DrawLatexNDC(xpos, ypos, text)
    else:
        label.DrawLatex(xpos, ypos, text)
    return
