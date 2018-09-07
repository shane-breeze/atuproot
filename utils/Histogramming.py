import copy
import numpy as np
import os
import pickle
from .Lambda import Lambda

class Histogram(object):
    def __init__(self, name="h", variables=[], bins=[], weight="ev: 1.", selection=[]):
        self.name = name
        self.variables = variables
        self.bins = bins
        self.weight = weight
        self.selection = selection

        self.string_to_func = {}
        self.histogram = {}

    def begin(self, event):
        functions = [var for var in self.variables+[self.weight]+self.selection]
        self.string_to_func = {f: Lambda(f) for f in functions}

    def end(self):
        self.string_to_func = {}

    def event(self, event):
        selection = reduce(lambda x,y: x & y, [
            self.string_to_func[s](event)
            for s in self.selection
        ]) if len(self.selection)>0 else True

        weight = self.string_to_func[self.weight](event)[selection]

        variables = []
        for v in self.variables:
            try:
                variables.append(self.string_to_func[v](event)[selection])
            except AttributeError:
                variables.append(np.array([]))

        weights1 = weight
        weights2 = weight**2

        variables = np.transpose(np.array(variables))
        bins = [np.array(b) for b in self.bins]

        hist_counts, hist_bins = np.histogramdd(variables, bins=bins)
        hist_yields = np.histogramdd(variables, bins=bins, weights=weights1)[0]
        hist_variance = np.histogramdd(variables, bins=bins, weights=weights2)[0]

        if self.histogram == {}:
            self.histogram = {
                "bins": hist_bins,
                "counts": hist_counts,
                "yields": hist_yields,
                "variance": hist_variance,
            }
        else:
            if not np.array_equal(hist_bins, self.histogram["bins"]):
                print(hist_bins)
                print(self.histogram["bins"])
            assert np.array_equal(hist_bins, self.histogram["bins"])
            self.histogram["counts"] += hist_counts
            self.histogram["yields"] += hist_yields
            self.histogram["variance"] += hist_variance

    def merge(self, other):
        if self.name != other.name:
            return

        self.histogram = {
            "bins": self.histogram["bins"],
            "counts": self.histogram["counts"] + other.histogram["counts"],
            "yields": self.histogram["yields"] + other.histogram["yields"],
            "variance": self.histogram["variance"] + other.histogram["variance"],
        }

    def save(self, outdir):
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        path = os.path.join(outdir, self.name + ".pkl")
        with open(path, 'w') as f:
            pickle.dump(self.histogram, f)

    def reload(self, path):
        if not os.path.exists(path):
            raise ValueError("{} does not exist".format(path))

        with open(path, 'r') as f:
            self.histogram = pickle.load(f)

    def __add__(self, other):
        assert self.name == other.name

        new_histogram = Histogram(self.name)
        new_histogram.histogram = {
            "bins": self.histogram["bins"],
            "counts": self.histogram["counts"] + other.histogram["counts"],
            "yields": self.histogram["yields"] + other.histogram["yields"],
            "variance": self.histogram["variance"] + other.histogram["variance"],
        }
        return new_histogram

class Histograms(object):
    def __init__(self):
        self.histograms = []

    def append(self, identifier, histogram):
        self.histograms.append((identifier, histogram))
        return self

    def extend(self, id_hists):
        self.histograms.extend(id_hists)
        return self

    def __getitem__(self, identifier):
        try:
            return next(h for n, h in self.histograms if n==identifier)
        except StopIteration:
            raise KeyError("{} not found".format(identifier))

    def begin(self, event, parents, selection):
        self.histograms = [((n[0], n[1], p, n[3]), copy.deepcopy(h))
                           for n, h in self.histograms
                           for p in parents]
        for n, h in self.histograms:
            if n[2] in selection:
                h.selection += selection[n[2]]
            h.begin(event)
        return self

    def end(self):
        for n, h in self.histograms:
            h.end()
        return self

    def event(self, event):
        for n, h in self.histograms:
            h.event(event)
        return self

    def merge(self, other):
        names = []
        for n, h in self.histograms:
            try:
                h.merge(other[n])
            except KeyError:
                pass
            names.append(n)

        for on, oh in other.histograms:
            if on in names:
                continue
            self.append(on, oh)
        return self

    def save(self, outdir):
        for n, h in self.histograms:
            args = [outdir]+list(n)
            path = os.path.join(*args)
            h.save(os.path.dirname(path))
        return self

    def reload(self, path):
        for dirpath, dirnames, filenames in os.walk(path):
            if "plot" in dirpath or len(filenames)==0:
                continue

            for filename in filenames:
                identifier = tuple(dirpath.split("/")[2:] + [os.path.splitext(filename)[0]])
                histogram = Histogram(identifier[-1])
                histogram.reload(os.path.join(dirpath, filename))
                self.append(identifier, histogram)
        return self
