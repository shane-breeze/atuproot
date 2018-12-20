import uproot
import awkward
import numpy as np
import mmap

from alphatwirl.loop.splitfuncs import create_files_start_length_list

from .BEvents import BEvents

class TreeChain(object):
    def __init__(self, input_paths, treename):
        self.input_paths = input_paths
        self.treename = treename

        self.tree_cache = {}
        self.tree_key_cache = self.load_tree(input_paths[0]).keys()
        self.tree_len_cache = {}

        self.total_len = 0
        self.total_len = sum(self.get_tree_len(path) for path in input_paths)
        self.entry_boundaries = [0]+list(np.cumsum([
            self.tree_len_cache[path] for path in input_paths
        ]))

    def load_tree(self, path):
        if path in self.tree_cache:
            tree = self.tree_cache[path]
        else:
            try:
                rootfile = uproot.open(path)
                tree = rootfile[self.treename]
            except mmap.error:
                def localsource(path):
                    return uproot.FileSource(path, **uproot.FileSource.defaults)
                rootfile = uproot.open(path, localsource=localsource)
                tree = rootfile [self.treename]
            self.tree_cache[path] = tree
        return tree

    def close_tree(self, path):
        if path in self.tree_cache:
            self.tree_cache.pop(path)
        return

    def get_tree_len(self, path):
        if path in self.tree_len_cache:
            tree_len = self.tree_len_cache[path]
        else:
            tree_len = len(self.load_tree(path))
            self.tree_len_cache[path] = tree_len
        return tree_len

    def __len__(self):
        return self.total_len

    def keys(self):
        return self.tree_key_cache

    def start_stop_path_list(self, start, stop):
        ssp_list = []
        for idx, (low_bound, upp_bound) in enumerate(zip(self.entry_boundaries[:-1],
                                                         self.entry_boundaries[1:])):
            path = self.input_paths[idx]

            if low_bound < start and upp_bound <= start:
                self.close_tree(path)
            elif low_bound < start and start < upp_bound <= stop:
                ssp_list.append((start-low_bound, upp_bound-low_bound, path))
            elif low_bound < start and stop < upp_bound:
                ssp_list.append((start-low_bound, stop-low_bound, path))
            elif start <= low_bound < stop and start < upp_bound <= stop:
                ssp_list.append((0, upp_bound-low_bound, path))
            elif start <= low_bound < stop and stop < upp_bound:
                ssp_list.append((0, stop-low_bound, path))
            else:
                pass

        return ssp_list

    def array(self, branch, entrystart, entrystop):
        arrays = []
        for start, stop, path in self.start_stop_path_list(entrystart, entrystop):
            tree = self.load_tree(path)
            arrays.append(tree.array(
                branch,
                entrystart = start,
                entrystop = stop,
            ))
        array = np.concatenate(arrays)
        if isinstance(arrays[0], awkward.JaggedArray):
            array = awkward.JaggedArray.fromiter(array)
        return array

class EventBuilder(object):
    def __init__(self, config):
        self.config = config

    def __repr__(self):
        return '{}({!r})'.format(
            self.__class__.__name__,
            self.config,
        )

    def __call__(self):
        tree = TreeChain(self.config.inputPaths, self.config.treeName)

        # if len(self.config.inputPaths) != 1:
        #     # TODO - support multiple inputPaths
        #     raise AttributeError("Multiple inputPaths not yet supported")

        # # Try to open the tree - some machines have configured limitations
        # # which prevent memmaps from begin created. Use a fallback - the
        # # localsource option
        # try:
        #     rootfile = uproot.open(self.config.inputPaths[0])
        #     tree = rootfile[self.config.treeName]
        # except:
        #     rootfile = uproot.open(self.config.inputPaths[0],
        #                        localsource = uproot.FileSource.defaults)
        #     tree = rootfile [self.config.treeName]

        events = BEvents(tree,
                         self.config.nevents_per_block,
                         self.config.start_block,
                         self.config.stop_block)
        events.config = self.config
        return events
