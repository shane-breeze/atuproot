from alphatwirl.loop import EventDatasetReader
import logging

class CustomEventDatasetReader(EventDatasetReader):
    def __init__(
        self, eventLoopRunner, reader, collector, split_into_build_events,
    ):
        self.merged_runids = []
        super(CustomEventDatasetReader, self).__init__(
            eventLoopRunner, reader, collector, split_into_build_events,
        )

    def _merge(self, runid, reader):
        self.merged_runids.append(runid)
        logger = logging.getLogger(__name__)
        logger.info("Merging reader of runid {} ({} remaining)".format(runid, len(self.runids)-len(self.merged_runids)))
        super(CustomEventDatasetReader, self)._merge(runid, reader)
