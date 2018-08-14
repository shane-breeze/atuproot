import collections
import uproot

EventBuilderConfig = collections.namedtuple(
    'EventBuilderConfig',
    'inputPaths treeName maxEvents start blocksize dataset name'
)

class EventBuilderConfigMaker(object):
    def __init__(self, blocksize):
        self.blocksize = blocksize

    def create_config_for(self, dataset, files, start, length):
        config = EventBuilderConfig(
            inputPaths = files,
            treeName = dataset.tree,
            maxEvents = length,
            start = start,
            blocksize = self.blocksize,
            dataset = dataset,
            name = dataset.name,
        )
        return config

    def file_list_in(self, dataset, maxFiles):
        if maxFiles < 0:
            return dataset.files
        return dataset.files[:min(maxFiles, len(dataset.files))]

    def nevents_in_file(self, path):
        try:
            return len(uproot.open(path)[self.treeName])
        except:
            return len(uproot.open(path, localsource=uproot.FileSource.defaults)[self.treeName])
