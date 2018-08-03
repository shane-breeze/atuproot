import os
import numpy as np
import pandas as pd
np.set_printoptions(threshold='nan')

from collections import OrderedDict as odict

class TestReader(object):
    def __init__(self, **kwargs):
        self.cutflows = ["Monojet", "SingleMuon", "DoubleMuon"]
        self.variables = ["Weight", "METnoX_pt", "DiMuon_pt", "METnoX_diMuonParaProjPt", "METnoX_diMuonPerpProjPt"]

    def begin(self, event):
        for cutflow in self.cutflows:
            for var in self.variables:
                setattr(self, "{}_{}".format(var, cutflow), None)

    def event(self, event):
        for cutflow in self.cutflows:
            for var in self.variables:
                setattr(event,
                        "{}_{}".format(var, cutflow),
                        getattr(event, var)[
                            getattr(event, "Cutflow_{}".format(cutflow)),
                        ])
        self.merge(event)

    def merge(self, other):
        for cutflow in self.cutflows:
            for var in self.variables:
                attr = "{}_{}".format(var, cutflow)
                setattr(self, attr,
                        np_merge(getattr(self, attr), getattr(other, attr)))

def np_merge(self, other):
    return other if self is None else np.concatenate((self, other))

class TestCollector(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.outdir = "output"
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

    def collect(self, dataset_readers_list):
        for dataset, readers in dataset_readers_list:
            for cutflow in readers[0].cutflows:
                data = odict([
                    (var, getattr(readers[0], "{}_{}".format(var, cutflow)))
                    for var in readers[0].variables
                ])
                df = pd.DataFrame(data)

                outdir = os.path.join(self.outdir, cutflow)
                if not os.path.exists(outdir):
                    os.makedirs(outdir)

                path = os.path.join(outdir, dataset+".pkl")
                df.to_pickle(path)
        return dataset_readers_list

test_reader = TestReader()
test_collector = TestCollector()

reader_collectors = [
    (test_reader, test_collector),
]
