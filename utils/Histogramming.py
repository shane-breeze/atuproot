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

        self.functions = [var for var in variables+[weight]+selection]
        self.string_to_func = {}

        self.histogram = {}

    def begin(self, event):
        self.string_to_func = {
            f: Lambda(f)
            for f in self.functions
        }

    def end(self):
        self.string_to_func = {}

    def event(self, event):
        selection = reduce(lambda x,y: x & y, [
            self.string_to_func[s](event)
            for s in self.selection
        ])

        weights = self.string_to_func[self.weight](event)[selection]
        variables = [self.string_to_func[v](event)[selection]
                     for v in self.variables]

        bins = self.bins
        weights1 = [weights]*len(variables)
        weights2 = [weights**2]*len(variables)

        if len(variables) == 1:
            variables = variables[0]
            bins = bins[0]
            weights1 = weights1[0]
            weights2 = weights2[0]

        hist_counts, hist_bins = np.histogram(variables, bins=bins)
        hist_yields = np.histogram(variables, bins=bins, weights=weights1)[0]
        hist_variance = np.histogram(variables, bins=bins, weights=weights2)[0]

        self.histogram = {
            "bins": hist_bins,
            "counts": hist_counts,
            "yields": hist_yields,
            "variance": hist_variance,
        }

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

    def begin(self, event):
        p = event.config.dataset.parent
        self.histograms = [((n[0], n[1], p, n[3]), h) for n, h in self.histograms]
        for n, h in self.histograms:
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
