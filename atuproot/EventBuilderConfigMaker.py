import os
import collections
import uproot

EventBuilderConfig = collections.namedtuple(
    'EventBuilderConfig',
    'inputPaths treeName start_block stop_block nevents_per_block dataset name branch_cache uproot_kwargs'
)

class EventBuilderConfigMaker(object):
    def __init__(
        self, nevents_per_block, treename_of_files_map={}, branch_cache={},
        uproot_kwargs={},
    ):
        self.nevents_per_block = nevents_per_block
        self._treename_of_files_map = treename_of_files_map

        self._nevents_in_file_cache = {}
        self._branch_cache = branch_cache
        self.uproot_kwargs = uproot_kwargs

    def create_config_for(self, dataset, files, start, length):
        config = EventBuilderConfig(
            inputPaths = files,
            treeName = dataset.tree,
            start_block = start,
            stop_block = length,
            nevents_per_block = self.nevents_per_block,
            dataset = dataset,
            name = dataset.name,
            branch_cache = self._branch_cache,
            uproot_kwargs = self.uproot_kwargs,
        )
        return config

    def file_list_in(self, dataset, maxFiles):
        if maxFiles < 0:
            return dataset.files
        return dataset.files[:min(maxFiles, len(dataset.files))]

    def nevents_in_file(self, path):
        path = os.path.abspath(path)
        if path not in self._nevents_in_file_cache:
            # Try to open root file with standard memmap with uproot. Use
            # localsource option if it fails
            try:
                rootfile = uproot.open(path)
            except:
                rootfile = uproot.open(
                    path,
                    localsource=lambda p: uproot.FileSource(p, **uproot.FileSource.defaults),
                )
            nevents = rootfile[self._treename_of_files_map[path]].numentries
            nblocks = int((nevents-1) / self.nevents_per_block + 1)
            self._nevents_in_file_cache[path] = nblocks
        return self._nevents_in_file_cache[path]
