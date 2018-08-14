import logging

class BEvents(object):
    def __init__(self, tree, blocksize=1000000, maxBlocks=-1, start=0):
        self.tree = tree
        self.nEvents = len(tree)
        self.blocksize = int(blocksize) if blocksize >= 0 else self.nEvents

        nBlocks = int((self.nEvents-1) / self.blocksize + 1)
        start = min(nBlocks, start)
        if maxBlocks > -1:
            self.nBlocks = min(nBlocks-start, maxBlocks)
        else:
            self.nBlocks = nBlocks-start
        self.maxBlocks = maxBlocks
        self.start = start
        self.iBlock = -1

        self._branch_cache = {}

    def __len__(self):
        return self.nBlocks

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            self._repr_content(),
        )

    def _repr_content(self):
        return 'tree = {!r}, nEvents = {!r}, nBlocks = {!r}, blocksize = {!r}, iBlock = {!r}'.format(
            self.tree,
            self.nEvents,
            self.nBlocks,
            self.blocksize,
            self.iBlock,
        )

    def __getitem__(self, i):
        if i >= self.nBlocks:
            self.iBlock = -1
            raise IndexError("The index is out of range: " + str(i))
        self._branch_cache = {}

        self.iBlock = i
        return self

    def __iter__(self):
        for self.iBlock in range(self.nBlocks):
            #sizes = {}
            #for k, v in self._branch_cache.items():
            #    size = 0
            #    if hasattr(v, "content"):
            #        size += v.content.nbytes
            #        size += v.starts.nbytes
            #        size += v.stops.nbytes
            #    elif hasattr(v, "nbytes"):
            #        size += v.nbytes
            #    sizes[k] = size
            #logger = logging.getLogger(__name__)
            #for (k, v) in sorted([(k, v) for k, v in sizes.items()], key=lambda x: x[1]):
            #    logger.info("Memory of {} = {} MB".format(k, v / (1024*1024.)))
            #total = sum([v for k, v in sizes.items()])
            #logger.info("Memory of _branch_cache = {} MB".format(total / (1024*1024.)))

            self._branch_cache = {}
            yield self
        self.iBlock = -1

    def __getattr__(self, attr):
        if attr in ["tree", "nEvents", "blocksize", "nBlocks", "maxBlocks",
                    "start", "iBlock", "_branch_cache", "entrystart",
                    "entrystop", "size"]:
            return getattr(self, attr)
        return self._get_branch(attr)

    def __setattr__(self, attr, val):
        if attr in ["tree", "nEvents", "blocksize", "nBlocks", "maxBlocks",
                    "start", "iBlock", "_branch_cache", "entrystart",
                    "entrystop", "size"]:
            super(BEvents, self).__setattr__(attr, val)
        else:
            self._branch_cache[attr] = val

    def _get_branch(self, name):
        if name in self._branch_cache:
            branch = self._branch_cache[name]
        else:
            self.entrystart = (self.start + self.iBlock) * self.blocksize
            self.entrystop = min(
                (self.start + self.iBlock + 1) * self.blocksize,
                (self.start + self.nBlocks) * self.blocksize,
                self.nEvents,
            )
            self.size = self.entrystop - self.entrystart
            branch = self.tree.array(name,
                                     entrystart = self.entrystart,
                                     entrystop = self.entrystop)
            self._branch_cache[name] = branch
        return branch

    def hasbranch(self, branch):
        return (branch in self.tree.keys() or branch in self._branch_cache)

    def delete_branches(self, branches):
        for branch in branches:
            if branch in self._branch_cache:
                self._branch_cache[branch] = None
                del self._branch_cache[branch]
