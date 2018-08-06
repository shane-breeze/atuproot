from utils.Lambda import Lambda
from . import Collection

class SkimCollections(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def begin(self, event):
        self.selection_functions = {k: Lambda(v)
                               for k, v in self.selection_dict.items()}

    def event(self, event):
        for (input_collection, output_collection), selection in self.selection_functions.items():
            setattr(event, output_collection,
                    Collection(output_collection, event, input_collection,
                               getattr(event, input_collection)(selection)))

    def end(self):
        self.selection_functions = {}
