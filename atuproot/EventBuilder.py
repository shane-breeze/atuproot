import uproot

from .BEvents import BEvents

class EventBuilder(object):
    def __init__(self, config):
        self.config = config

    def __repr__(self):
        return '{}({!r})'.format(
            self.__class__.__name__,
            self.config,
        )

    def __call__(self):
        if len(self.config.inputPaths) != 1:
            raise AttributeError("Multiple inputPaths not yet supported")
        try:
            tree = uproot.open(self.config.inputPaths[0])[self.config.treeName]
        except:
            tree = uproot.open(self.config.inputPaths[0], localsource=uproot.FileSource.defaults)[self.config.treeName]
        events = BEvents(tree,
                         self.config.blocksize,
                         self.config.maxBlocks,
                         self.config.start)
        events.config = self.config
        return events
