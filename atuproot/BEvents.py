import operator
from cachetools import cachedmethod
from cachetools.keys import hashkey
from functools import partial

import numpy as np
import awkward as awk

class BEvents(object):
    non_branch_attrs = [
        "tree", "nevents_in_tree", "nevents_per_block", "nblocks",
        "start_block", "stop_block", "iblock", "start_entry", "stop_entry",
        "_branch_cache", "_nonbranch_cache", "size", "config",
    ]
    def __init__(
        self, tree, nevents_per_block=100000, start_block=0, stop_block=-1,
        branch_cache = {},
    ):
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

        self._branch_cache = branch_cache
        self._nonbranch_cache = {}

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
                key = hashkey('BEvents._get_branch', attr)
                self._branch_cache[key] = val

    @cachedmethod(operator.attrgetter('_branch_cache'), key=partial(hashkey, 'BEvents._get_branch'))
    def _get_branch(self, name):
        self.start_entry = (self.start_block + self.iblock) * self.nevents_per_block
        self.stop_entry= min(
            (self.start_block + self.iblock + 1) * self.nevents_per_block,
            (self.start_block + self.nblocks) * self.nevents_per_block,
            self.nevents_in_tree,
        )
        self.size = self.stop_entry - self.start_entry
        try:
            branch = self.tree.array(
                name,
                entrystart = self.start_entry,
                entrystop = self.stop_entry,
            )
        except KeyError as e:
            raise AttributeError(e)
        return branch

    def hasbranch(self, branch, encoding='utf-8'):
        return (
            branch.encode(encoding) in self.tree.keys()
            or hashkey('BEvents._get_branch', branch) in self._branch_cache
            or branch in self._nonbranch_cache
        )

    def delete_branches(self, branches):
        for branch in branches:
            key = hashkey('BEvents._get_branch', branch)
            if key in self._branch_cache:
                self._branch_cache.popitem(key)
            elif branch in self._nonbranch_cache:
                self._nonbranch_cache.popitem(branch)
