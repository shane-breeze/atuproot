import ROOT as r

def cms_tdr_style():
    plot_style = r.TStyle()

    # Canvas
    plot_style.SetCanvasBorderMode(0)
    plot_style.SetCanvasColor(r.kWhite)
    plot_style.SetCanvasDefW(650)
    plot_style.SetCanvasDefH(750)
    plot_style.SetCanvasDefX(0)
    plot_style.SetCanvasDefY(0)

    plot_style.SetPadBorderMode(0)
    plot_style.SetPadColor(r.kWhite)
    plot_style.SetPadGridX(False)
    plot_style.SetPadGridY(False)
    plot_style.SetGridColor(0)
    plot_style.SetGridStyle(3)
    plot_style.SetGridWidth(1)

    # Frame
    plot_style.SetFrameBorderMode(0)
    plot_style.SetFrameBorderSize(1)
    plot_style.SetFrameFillColor(0)
    plot_style.SetFrameFillStyle(0)
    plot_style.SetFrameLineColor(1)
    plot_style.SetFrameLineStyle(1)
    plot_style.SetFrameLineWidth(1)

    # Histogram
    #plot_style.SetHistFillColor(1)
    #plot_style.SetHistFillStyle(0)
    plot_style.SetHistLineColor(1)
    plot_style.SetHistLineStyle(0)
    plot_style.SetHistLineWidth(2)
    #plot_style.SetNumberContours(Int_t number = 20)

    plot_style.SetEndErrorSize(2)
    #plot_style.SetErrorMarker(20)
    #plot_style.SetErrorX(0.)

    plot_style.SetMarkerStyle(20)

    # Fit/Function:
    plot_style.SetOptFit(1)
    plot_style.SetFitFormat("5.4g")
    plot_style.SetFuncColor(2)
    plot_style.SetFuncStyle(1)
    plot_style.SetFuncWidth(1)

    # Date:
    plot_style.SetOptDate(0)
    #plot_style.SetDateX(Float_t x = 0.01)
    #plot_style.SetDateY(Float_t y = 0.01)

    # Statistics box:
    plot_style.SetOptFile(0)
    plot_style.SetOptStat(0) # To display the mean and RMS:   SetOptStat("mr")
    plot_style.SetStatColor(r.kWhite)
    plot_style.SetStatFont(42)
    plot_style.SetStatFontSize(0.025)
    plot_style.SetStatTextColor(1)
    plot_style.SetStatFormat("6.4g")
    plot_style.SetStatBorderSize(1)
    plot_style.SetStatH(0.1)
    plot_style.SetStatW(0.15)
    #plot_style.SetStatStyle(Style_t style = 1001)
    #plot_style.SetStatX(Float_t x = 0)
    #plot_style.SetStatY(Float_t y = 0)

    # Margins
    plot_style.SetPadTopMargin(0.08)
    plot_style.SetPadLeftMargin(0.10)
    plot_style.SetPadRightMargin(0.05)
    plot_style.SetPadBottomMargin(0.10)

    # Global title
    plot_style.SetOptTitle(0)
    plot_style.SetTitleFont(42)
    plot_style.SetTitleColor(1)
    plot_style.SetTitleTextColor(1)
    plot_style.SetTitleFillColor(10)
    plot_style.SetTitleFontSize(0.05)
    #plot_style.SetTitleH(0) # Set the height of the title box
    #plot_style.SetTitleW(0) # Set the width of the title box
    #plot_style.SetTitleX(0) # Set the position of the title box
    #plot_style.SetTitleY(0.985) # Set the position of the title box
    #plot_style.SetTitleStyle(Style_t style = 1001)
    #plot_style.SetTitleBorderSize(2)

    # Axis titles

    plot_style.SetTitleColor(1, "XYZ")
    plot_style.SetTitleFont(42, "XYZ")
    plot_style.SetTitleSize(0.045, "XYZ")
    #plot_style.SetTitleXSize(Float_t size = 0.02) # Another way to set the size?
    #plot_style.SetTitleYSize(Float_t size = 0.02)
    plot_style.SetTitleXOffset(1.1)
    plot_style.SetTitleYOffset(1.25)
    #plot_style.SetTitleOffset(1.1, "Y") # Another way to set the Offset

    # Axis labels
    plot_style.SetLabelColor(1, "XYZ")
    plot_style.SetLabelFont(42, "XYZ")
    plot_style.SetLabelOffset(0.007, "XYZ")
    plot_style.SetLabelSize(0.035, "XYZ")

    # Axis
    plot_style.SetAxisColor(1, "XYZ")
    plot_style.SetStripDecimals(True)
    plot_style.SetTickLength(0.03, "XYZ")
    plot_style.SetNdivisions(510, "XYZ")
    plot_style.SetPadTickX(1)  # To get tick marks on the opposite side of the frame
    plot_style.SetPadTickY(1)

    # Log plots
    plot_style.SetOptLogx(0)
    plot_style.SetOptLogy(0)
    plot_style.SetOptLogz(0)

    # Postscript options
    plot_style.SetPaperSize(20.,20.)
    #plot_style.SetLineScalePS(Float_t scale = 3)
    #plot_style.SetLineStyleString(Int_t i, const char* text)
    #plot_style.SetHeaderPS(const char* header)
    #plot_style.SetTitlePS(const char* pstitle)

    #plot_style.SetBarOffset(Float_t baroff = 0.5)
    #plot_style.SetBarWidth(Float_t barwidth = 0.5)
    #plot_style.SetPaintTextFormat(const char* format = "g")
    #plot_style.SetPalette(Int_t ncolors = 0, Int_t* colors = 0)
    #plot_style.SetTimeOffset(Double_t toffset)
    #plot_style.SetHistMinimumZero(kTRUE)

    plot_style.SetHatchesLineWidth(5)
    plot_style.SetHatchesSpacing(0.05)

    # Legend
    plot_style.SetLegendBorderSize(0)
    plot_style.SetLegendFont(42)
    plot_style.SetLegendTextSize(0.035)

    plot_style.cd()
