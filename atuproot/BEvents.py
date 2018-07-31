class BEvents(object):
    def __init__(self, tree, blocksize=1000000):
        self.tree = tree
        self.nEvents = len(tree)
        self.blocksize = int(blocksize) if blocksize >= 0 else self.nEvents
        self.iBlock = -1
        self.nBlocks = int((self.nEvents-1) / self.blocksize + 1)

        self._branch_cache = {}

    def __len__(self):
        return self.nBlocks

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            self._repr_contents(),
        )

    def _repr_contents(self):
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
            self._branch_cache = {}
            yield self
        self.iBlock = -1

    def __getattr__(self, attr):
        if attr in ["tree", "nEvents", "blocksize", "iBlock", "nBlocks",
                    "_branch_cache", "entrystart", "entrystop", "size"]:
            return getattr(self, attr)
        return self._get_branch(attr)

    def __setattr__(self, attr, val):
        if attr in ["tree", "nEvents", "blocksize", "iBlock", "nBlocks",
                    "_branch_cache", "entrystart", "entrystop", "size"]:
            super(BEvents, self).__setattr__(attr, val)
        else:
            self.set_branch(attr, val)

    def set_branch(self, name, branch):
        self._branch_cache[name] = branch

    def _get_branch(self, name):
        if name in self._branch_cache:
            branch = self._branch_cache[name]
        else:
            self.entrystart = self.iBlock * self.blocksize
            self.entrystop = min((self.iBlock+1) * self.blocksize, self.nEvents)
            self.size = self.entrystop - self.entrystart
            branch = self.tree.array(name,
                                     entrystart = self.entrystart,
                                     entrystop = self.entrystop)
            self._branch_cache[name] = branch
        return branch

    def hasbranch(self, branch):
        return (branch in self.tree.keys() or branch in self._branch_cache)
