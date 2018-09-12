class WeightXsLumi(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def begin(self, event):
        dataset = event.config.dataset
        sumweights = sum([associates.sumweights
                          for associates in dataset.associates])

        self.sf = (dataset.xsection * dataset.lumi / sumweights)

    def event(self, event):
        corrs = self.sf * event.genWeight
        event.Weight_XsLumi = corrs
        event.Weight_MET *= corrs
        event.Weight_SingleMuon *= corrs
        event.Weight_SingleElectron *= corrs
