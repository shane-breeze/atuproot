from sequence.sequence import sequence
from sequence.collectors import reader_collectors
from sequence.Modules import ScribblerWrapper
from alphatwirl.loop import NullCollector


def build_sequence(sequence_cfg_path):
    return [(ScribblerWrapper(reader), collector)
            for (reader, collector) in sequence]
