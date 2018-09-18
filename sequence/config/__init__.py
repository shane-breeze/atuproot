import imp
from sequence.Readers import ScribblerWrapper


def build_sequence(sequence_cfg_path):
    seq = imp.load_source('sequence.sequence', sequence_cfg_path)
    return [(ScribblerWrapper(reader), collector)
            for (reader, collector) in seq.sequence]
