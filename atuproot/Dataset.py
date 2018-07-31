import collections

class Dataset(object):
    args = ["name", "parent", "isdata", "xsection", "lumi", "energy",
            "sumweights", "files", "associates"]
    def __init__(self, **kwargs):
        for arg in self.args:
            setattr(self, arg, kwargs[arg])

    def __repr__(self):
        return "{}({}, {})".format(
            self.__class__.__name__,
            ", ".join(["{} = {!r}".format(k, getattr(self, k))
                       for k in self.args[:-2]]),
            "associates = {}".format(", ".join([associate.name
                                                for associate in self.associates])),
        )

#Dataset = collections.namedtuple('Dataset', 'name parent isdata xsection lumi energy sumweights files associates')
