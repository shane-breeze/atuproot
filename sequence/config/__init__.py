from sequence.sequence import sequence
from sequence.Readers import ScribblerWrapper

def build_sequence(sequence_cfg_path):
    return [(ScribblerWrapper(reader), collector)
            for (reader, collector) in sequence]
