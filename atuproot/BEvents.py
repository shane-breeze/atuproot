import mmap
import numpy as np
import awkward as awk
import uproot

class BEvents(object):
    non_branch_attrs = [
        "tree", "nevents_in_tree", "nevents_per_block", "nblocks",
        "start_block", "stop_block", "iblock", "start_entry", "stop_entry",
        "_branch_cache", "_nonbranch_cache", "size", "config",
    ]
    def __init__(self, config):
        self._branch_cache = config.branch_cache
        self.tree = self._build_tree(config)

        self.nevents_in_tree = len(self.tree)
        self.nevents_per_block = (
            int(config.nevents_per_block)
            if config.nevents_per_block >= 0 else
            self.nevents_in_tree
        )

        nblocks = int((self.nevents_in_tree-1)/self.nevents_per_block + 1)
        start_block = min(nblocks, config.start_block)
        if config.stop_block > -1:
            self.nblocks = min(nblocks-start_block, config.stop_block)
        else:
            self.nblocks = nblocks-start_block
        self.stop_block = config.stop_block
        self.start_block = start_block
        self.iblock = -1

        self._nonbranch_cache = {}
        self.config = config

    def _build_tree(self, config):
        args = (config.inputPaths, config.treeName)
        kwargs = dict(
            entrysteps=config.nevents_per_block,
            **config.uproot_kwargs,
        )

        # Try to open the tree - some machines have configured limitations
        # which prevent memmaps from begin created. Use a fallback - the
        # localsource option
        try:
            tree = uproot.lazyarrays(*args, **kwargs)
        except mmap.error:
            kwargs["localsource"] = lambda p: uproot.FileSource(p, **uproot.FileSource.defaults),
            tree = uproot.lazyarrays(*args, **kwargs)
        return tree

    def __len__(self):
        return self.nblocks

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            self._repr_content(),
        )

    def _repr_content(self):
        return (
            'tree = {!r}, nevents_in_tree = {!r}, nevents_per_block = {!r}, '
            'nblocks = {!r}, iblock = {!r}, start_block = {!r}, '
            'stop_block = {!r}'.format(
                self.tree,
                self.nevents_in_tree,
                self.nevents_per_block,
                self.nblocks,
                self.iblock,
                self.start_block,
                self.stop_block,
            )
        )

    def __getitem__(self, i):
        if i >= self.nblocks:
            self.iblock = -1
            raise IndexError("The index is out of range: " + str(i))
        self._branch_cache.clear()

        self.iblock = i
        return self

    def __iter__(self):
        for self.iblock in range(self.nblocks):
            self._branch_cache.clear()
            yield self
        self.iblock = -1
        self._nonbranch_cache = {}

    def __getattr__(self, attr):
        if attr in self.non_branch_attrs:
            return getattr(self, attr)
        elif attr in self._nonbranch_cache:
            return self._nonbranch_cache[attr]
        return self._get_branch(attr)

    def __setattr__(self, attr, val):
        if attr in self.non_branch_attrs:
            super(BEvents, self).__setattr__(attr, val)
        else:
            if not (isinstance(val, awk.JaggedArray) or isinstance(val, np.ndarray)):
                self._nonbranch_cache[attr] = val
            else:
                self._branch_cache[attr] = val

    def _get_branch(self, name):
        self.start_entry = (self.start_block + self.iblock) * self.nevents_per_block
        self.stop_entry = min(
            (self.start_block + self.iblock + 1) * self.nevents_per_block,
            (self.start_block + self.nblocks) * self.nevents_per_block,
            self.nevents_in_tree,
        )
        self.size = self.stop_entry - self.start_entry
        return getattr(self.tree[self.start_entry:self.stop_entry], name)

    def hasbranch(self, branch):
        return (
            branch in self.tree.keys()
            or branch in self._branch_cache
            or branch in self._nonbranch_cache
        )

    def delete_branches(self, branches):
        for branch in branches:
            if branch in self._branch_cache:
                self._branch_cache.popitem(branch)
            elif branch in self._nonbranch_cache:
                self._nonbranch_cache.popitem(branch)
