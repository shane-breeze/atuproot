def set_hist_style(hist, kind="data"):
    hist.linecolor = "black"
    hist.linestyle = 1
    hist.linewidth = 2
    hist.markersize = 1.
    hist.markercolor = "black"

    if kind == "data":
        hist.drawstyle = "e1"
        hist.legendstyle = "lp"
        hist.fillcolor = "black"
        hist.fillstyle = 0
        hist.markerstyle = 20
    elif kind == "mc":
        hist.drawstyle = "hist"
        hist.legendstyle = "f"
        hist.fillcolor = "blue"
        hist.fillstyle = 0
        hist.markerstyle = 0

    xaxis = hist.xaxis
    xaxis.axiscolor = "black"
    xaxis.labelcolor = "black"
    xaxis.labelfont = "42"
    xaxis.labeloffset = 1.0
    xaxis.labelsize = 0.04
    xaxis.ndivisions = 5 + 5*100 + 0*10000
    xaxis.ticklength = 0.03
    xaxis.titlecolor = "black"
    xaxis.titlefont = "42"
    xaxis.set_title_offset(0.95)
    xaxis.titlesize = 0.045

    yaxis = hist.yaxis
    yaxis.axiscolor = "black"
    yaxis.labelcolor = "black"
    yaxis.labelfont = "42"
    yaxis.labeloffset = 1.0
    yaxis.labelsize = 0.04
    yaxis.ndivisions = 5 + 5*100 + 0*10000
    yaxis.ticklength = 0.03
    yaxis.titlecolor = "black"
    yaxis.titlefont = "42"
    yaxis.set_title_offset(1.0)
    yaxis.titlesize = 0.045
