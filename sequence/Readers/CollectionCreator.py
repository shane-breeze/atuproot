import numpy as np
import uproot
from numba import njit, int32

@njit
def create_boundaries(selection, starts, stops):
    nev = stops.shape[0]
    new_starts = np.zeros(nev, dtype=int32)
    new_stops = np.zeros(nev, dtype=int32)

    count = 0
    for iev, (start, stop) in enumerate(zip(starts, stops)):
        new_starts[iev] = count
        for iobj in range(start, stop):
            if selection[iobj]:
                count += 1
        new_stops[iev] = count

    return new_starts, new_stops

class Collection(object):
    def __init__(self, name, event, ref_name=None, selection=None):
        self.name = name
        self.event = event
        self.ref_name = ref_name
        self.selection = selection

    def __getattr__(self, attr):
        if attr in ["name", "event", "ref_name", "selection"]:
            raise AttributeError("{} should be defined but isn't".format(attr))

        branch_name = self.name+"_"+attr
        if not self.event.hasbranch(branch_name) and self.ref_name is not None:
            branch = self.create_branch(attr)
            setattr(self.event, branch_name, branch)
        return getattr(self.event, branch_name)

    @property
    def size(self):
        return self.pt.stops - self.pt.starts

    @property
    def starts(self):
        return self.pt.starts

    @property
    def stops(self):
        return self.pt.stops

    def create_branch(self, attr):
        ref_branch = getattr(getattr(self.event, self.ref_name), attr)

        if hasattr(ref_branch, "starts"):
            new_starts, new_stops = create_boundaries(
                self.selection, ref_branch.starts, ref_branch.stops,
            )

            array = uproot.interp.jagged.JaggedArray(
                ref_branch.content[self.selection],
                new_starts,
                new_stops,
            )
        else:
            array = ref_branch[self.selection]

        return array

    def __call__(self, func):
        return self.apply_selection(func)

    def __repr__(self):
        return "{}(name = {!r}, ref_name = {!r}, selection = {!r})".format(
            self.__class__.__name__,
            self.name,
            self.ref_name,
            self.selection,
        )

    def apply_selection(self, func):
        class CollectionWrapper(object):
            def __init__(self, collection):
                self.collection = collection

            def __getattr__(self, attr):
                result = getattr(self.collection, attr)
                return result.content

        temp_collection = CollectionWrapper(self)
        return func(temp_collection)

class CollectionCreator(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def event(self, event):
        for collection in self.collections:
            setattr(event, collection, Collection(collection, event))
