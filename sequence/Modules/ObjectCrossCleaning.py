import uproot
import numpy as np
from numpy import pi
from numba import njit
from CollectionCreator import Collection

from utils.Geometry import DeltaR2

class ObjectCrossCleaning(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def event(self, event):
        for ref_collection_name in self.ref_collections:
            ref_collection = getattr(event, ref_collection_name)
            for clean_collection_name in self.clean_collections:
                clean_collection = getattr(event, clean_collection_name)

                selection = comp(*setup_comp(clean_collection, ref_collection))
                output_collection = clean_collection_name+"Clean"
                setattr(event, output_collection,
                        Collection(output_collection, event,
                                   clean_collection_name, selection))

def setup_comp(coll1, coll2):
    etas1, phis1 = coll1.eta, coll1.phi
    etas2, phis2 = coll2.eta, coll2.phi
    nev = etas1.starts.shape[0]
    contents = np.ones(etas1.stops[-1], dtype=bool)
    return etas1.contents, etas2.contents, phis1.contents, phis2.contents,\
           etas1.starts, etas2.starts,\
           etas1.stops-etas1.starts, etas2.stops-etas2.starts,\
           nev, contents

@njit(cache=True)
def comp(etas1_cont, etas2_cont, phis1_cont, phis2_cont,
         starts_1, starts_2, lens_1, lens_2, nev, contents):

    # event loop
    for iev in range(nev):

        # loop over jets
        for ij in range(lens_1[iev]):
            rij = starts_1[iev]+ij
            jeta = etas1_cont[rij]
            jphi = phis1_cont[rij]

            # loop over muons
            for iu in range(lens_2[iev]):
                riu = starts_2[iev]+iu
                deta = jeta - etas2_cont[riu]
                dphi = jphi - phis2_cont[riu]

                # Bound phi
                #if dphi >= pi:
                #    dphi -= 2*pi
                #elif dphi < -pi:
                #    dphi += 2*pi

                # delta r**2 < (0.4)**2 -> matched
                #if deta**2 + dphi**2 < 0.16:
                if DeltaR2(deta, dphi) < 0.16:
                    contents[rij] = False
                    break

    return contents
