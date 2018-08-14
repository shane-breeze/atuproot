from sequence.sequence import sequence
from sequence.collectors import reader_collectors
from sequence.Modules import ScribblerWrapper
from alphatwirl.loop import NullCollector


def build_sequence(sequence_cfg_path):
    return [(ScribblerWrapper(module), NullCollector())
                           for module in sequence] + reader_collectors
