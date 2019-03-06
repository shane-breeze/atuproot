from alphatwirl.loop import ReaderComposite

class CustomReaderComposite(ReaderComposite):
    def merge(self, other):
        if not hasattr(other, "readers"):
            return
        super(CustomReaderComposite, self).merge(other)
