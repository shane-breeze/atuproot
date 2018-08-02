from alphatwirl.loop import NullCollector
from atuproot.AtUproot import AtUproot

from sequence.sequence import sequence
from sequence.collectors import reader_collectors
from datasets.datasets import get_datasets
from sequence.Modules import ScribblerWrapper

#import logging
#logging.getLogger("ROOT.TClass.Init").setLevel(logging.ERROR)
#
#from rootpy import log
#log_mpl = log["/matplotlib"]
#log_mpl.setLevel(log_mpl.info)
#
#logger = log["/"+__name__]
#logger.setLevel(log.INFO)

import argparse
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="output", type=str,
                        help="Where to save the results")
    parser.add_argument("--mode", default="multiprocessing", type=str,
                        help="Which mode to run in (multiprocessing, htcondor, sge)")
    parser.add_argument("--ncores", default=0, type=int,
                        help="Number of cores to run on")
    parser.add_argument("--nEventsPerSample", default=-1, type=int,
                        help="Number of events per sample")
    parser.add_argument("--blocksize", default=1000000, type=int,
                        help="Number of events per block")
    parser.add_argument("--data", default="MET", type=str,
                        help="Which dataset to run over")
    parser.add_argument("--quiet", default=False, action='store_true',
                        help="Keep progress report quiet")
    parser.add_argument("--profile", default=False, action='store_true',
                        help="Profile the code")
    parser.add_argument("--sample", default=None, type=str,
                        help="Select some sample")
    return parser.parse_args()

if __name__ == "__main__":
    options = parse_args()

    datasets = get_datasets()
    for dataset in datasets:
        if dataset.isdata and not dataset.parent == options.data:
            del dataset


    if options.sample is not None:
        datasets = [d for d in datasets
                    if d.name==options.sample or \
                       d.parent==options.sample]

    process = AtUproot(options.outdir,
        quiet = options.quiet,
        parallel_mode = options.mode,
        process = options.ncores,
        max_events_per_process = options.nEventsPerSample,
        blocksize = options.blocksize,
        profile = options.profile,
        profile_out_path = "profile.txt",
    )
    process.run(datasets, [(ScribblerWrapper(module), NullCollector())
                           for module in sequence] + reader_collectors)
