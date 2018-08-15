class WeightXsLumi(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def begin(self, event):
        self.xs = event.config.dataset.xsection
        self.lumi = event.config.dataset.lumi
        self.sumweights = sum([associates.sumweights
                               for associates in event.config.dataset.associates])

    def event(self, event):
        event.Weight *= (self.xs * self.lumi / self.sumweights) * event.genWeight
