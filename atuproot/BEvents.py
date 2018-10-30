import base64

class DummyBranch(object):
    def __init__(self, name, tree):
        self.name = name
        self.tree = tree

    def array(self, interpretation=None, entrystart=None, entrystop=None, flatten=False, cache=None, basketcache=None, keycache=None, executor=None, blocking=True):
        if cache is not None:
            cachekey = self._cachekey(entrystart, entrystop)
            out = cache.get(cachekey, None)
            if out is not None:
                return out
        return None

    def _cachekey(self, entrystart, entrystop):
	return "{0};{1};{2};{3}-{4}".format(
            base64.b64encode(self.tree._context.uuid).decode("ascii"),
            self.tree._context.treename.decode("ascii"),
            self.name.decode("ascii"),
            entrystart,
            entrystop,
        )


class BEvents(object):
    non_branch_attrs = ["tree", "nevents_in_tree", "nevents_per_block",
                        "nblocks", "start_block", "stop_block", "iblock",
                        "start_entry", "stop_entry", "cache", "size",
                        "config"]
    def __init__(self, tree,
                 nevents_per_block=100000,
                 start_block=0, stop_block=-1,
                 cache={}):
        self.tree = tree
        self.nevents_in_tree = len(tree)
        self.nevents_per_block = int(nevents_per_block) \
                if nevents_per_block >= 0 \
                else self.nevents_in_tree

        nblocks = int((self.nevents_in_tree-1)/self.nevents_per_block + 1)
        start_block = min(nblocks, start_block)
        if stop_block > -1:
            self.nblocks = min(nblocks-start_block, stop_block)
        else:
            self.nblocks = nblocks-start_block
        self.stop_block = stop_block
        self.start_block = start_block
        self.iblock = -1

        self.cache = cache

    def __len__(self):
        return self.nblocks

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            self._repr_content(),
        )

    def _repr_content(self):
        return 'tree = {!r}, nevents_in_tree = {!r}, nevents_per_block = {!r}, '\
                'nblocks = {!r}, iblock = {!r}, start_block = {!r}, '\
               'stop_block = {!r}'.format(
                   self.tree,
                   self.nevents_in_tree,
                   self.nevents_per_block,
                   self.nblocks,
                   self.iblock,
                   self.start_block,
                   self.stop_block,
               )

    def __getitem__(self, i):
        if i >= self.nblocks:
            self.iblock = -1
            raise IndexError("The index is out of range: " + str(i))

        self.iblock = i
        return self

    def __iter__(self):
        for self.iblock in range(self.nblocks):
            yield self
        self.iblock = -1

    def __getattr__(self, attr):
        if attr in self.non_branch_attrs:
            return getattr(self, attr)
        return self._get_branch(attr)

    def __setattr__(self, attr, val):
        if attr in self.non_branch_attrs:
            super(BEvents, self).__setattr__(attr, val)
        else:
            branch = DummyBranch(attr, self.tree)
            self.tree._branchlookup[attr] = branch
            self.cache[branch._cachekey(self.start_entry, self.stop_entry)] = val

    def _set_start_stops(self):
        self.start_entry = (self.start_block + self.iblock) * self.nevents_per_block
        self.stop_entry= min(
            (self.start_block + self.iblock + 1) * self.nevents_per_block,
            (self.start_block + self.nblocks) * self.nevents_per_block,
            self.nevents_in_tree,
        )
        self.size = self.stop_entry - self.start_entry

    def _get_branch(self, name):
        self._set_start_stops()
        branch = self.tree.array(
            name,
            entrystart = self.start_entry,
            entrystop = self.stop_entry,
            cache = self.cache,
        )
        return branch

    def get_branches(self, names):
        self._set_start_stops()
        branches = self.tree.pandas.df(
            names,
            flatten = True,
            entrystart = self.start_entry,
            entrystop = self.stop_entry,
            cache = self.cache,
        )
        return branches
