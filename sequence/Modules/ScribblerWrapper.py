class ScribblerWrapper(object):
    def __init__(self, scribbler):
        self.scribbler = scribbler
        self.data = getattr(self.scribbler, "data", True)
        self.mc = getattr(self.scribbler, "mc", True)

    def __getattr__(self, attr):
        if attr in ["scribbler", "data", "mc"]:
            raise AttributeError("{} should be assigned but isn't".format(attr))
        return getattr(self.scribbler, attr)

    def begin(self, event):
        self.isdata = event.config.dataset.isdata

        if self.isdata and not self.data:
            return True

        if not self.isdata and not self.mc:
            return True

        if hasattr(self.scribbler, "begin"):
            return self.scribbler.begin(event)

    def event(self, event):
        if self.isdata and not self.data:
            return True

        if not self.isdata and not self.mc:
            return True

        if hasattr(self.scribbler, "event"):
            return self.scribbler.event(event)
        return True
