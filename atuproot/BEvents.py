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

    def __getattr__(self, name):
        return self._get_branch(name)

    def _get_branch(self, name):
        if name in self._branch_cache:
            branch = self._branch_cache[name]
        else:
            self.entrystart = self.iBlock * self.blocksize
            self.entrystop = min((self.iBlock+1) * self.blocksize, self.nEvents)
            branch = self.tree.array(name,
                                     entrystart = self.entrystart,
                                     entrystop = self.entrystop)
        return branch

    def hasbranch(self, branch):
        return branch in self.tree.keys()
