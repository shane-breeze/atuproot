import uproot
import numpy as np
from numpy import pi
from numba import njit, boolean
from .CollectionCreator import Collection

from utils.Geometry import DeltaR2

class ObjectCrossCleaning(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def event(self, event):
        for clean_collection_name in self.clean_collections:
            clean_collection = getattr(event, clean_collection_name)

            selections = np.ones(clean_collection.stops[-1], dtype=bool)
            for ref_collection_name in self.ref_collections:
                ref_collection = getattr(event, ref_collection_name)
                selections = selections & comp(clean_collection, ref_collection)

            for name in ["Veto", "Selection"]:
                old_selection = getattr(event, clean_collection_name+name).selection
                new_selection = old_selection & selections
                getattr(event, clean_collection_name).selection = new_selection
            #output_collection = clean_collection_name+"Clean"
            #setattr(event, output_collection,
            #        Collection(output_collection, event,
            #                   clean_collection_name, selections))

def comp(coll1, coll2):
    return comp_jit(coll1.eta.content, coll1.phi.content,
                    coll1.starts, coll1.stops,
                    coll2.eta.content, coll2.phi.content,
                    coll2.starts, coll2.stops)

@njit
def comp_jit(etas1_cont, phis1_cont, starts_1, stops_1,
             etas2_cont, phis2_cont, starts_2, stops_2):
    content = np.ones(stops_1[-1], dtype=boolean)
    for iev, (start_1, stop_1, start_2, stop_2) in enumerate(zip(starts_1,
                                                                 stops_1,
                                                                 starts_2,
                                                                 stops_2)):
        for idx1 in range(start_1, stop_1):
            for idx2 in range(start_2, stop_2):
                deta = etas1_cont[idx1] - etas2_cont[idx2]
                dphi = phis1_cont[idx1] - phis2_cont[idx2]

                if DeltaR2(deta, dphi) < 0.16:
                    content[idx1] = False
                    break
    return content
