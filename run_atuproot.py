#!/usr/bin/env python
import warnings
warnings.filterwarnings('ignore')

from atuproot.AtUproot import AtUproot
from atuproot.build_parallel import build_parallel
from atuproot.utils import grouped_run
from datasets.datasets import get_datasets
from sequence.config import build_sequence

import logging
logging.getLogger(__name__).setLevel(logging.INFO)
logging.getLogger("alphatwirl").setLevel(logging.INFO)
logging.getLogger("atuproot.SGEJobSubmitter").setLevel(logging.INFO)

logging.getLogger(__name__).propagate = False
logging.getLogger("alphatwirl").propagate = False
logging.getLogger("atuproot.SGEJobSubmitter").propagate = False
logging.getLogger("atuproot.AtUproot").propagate = False

import argparse
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_cfg", type=str,
                        help="Dataset config to run over")
    parser.add_argument("sequence_cfg", type=str,
                        help="Config for how to process events")
    parser.add_argument("--outdir", default="output", type=str,
                        help="Where to save the results")
    parser.add_argument("--mode", default="multiprocessing", type=str,
                        help="Which mode to run in (multiprocessing, htcondor, "
                             "sge)")
    parser.add_argument("--ncores", default=0, type=int,
                        help="Number of cores to run on")
    parser.add_argument("--nblocks-per-dataset", default=-1, type=int,
                        help="Number of blocks per dataset")
    parser.add_argument("--nblocks-per-sample", default=-1, type=int,
                        help="Number of blocks per sample")
    parser.add_argument("--blocksize", default=1000000, type=int,
                        help="Number of events per block")
    parser.add_argument("--quiet", default=False, action='store_true',
                        help="Keep progress report quiet")
    parser.add_argument("--profile", default=False, action='store_true',
                        help="Profile the code")
    parser.add_argument("--sample", default=None, type=str,
                        help="Select some sample")
    parser.add_argument("--redraw", default=False, action='store_true',
                        help="Overrides most options. Runs over collectors "
                             "only to rerun the draw function on outdir")
    return parser.parse_args()

def run(sequence, datasets, options):
    process = AtUproot(options.outdir,
        quiet = options.quiet,
        parallel_mode = options.mode,
        process = options.ncores,
        max_blocks_per_dataset = options.nblocks_per_dataset,
        max_blocks_per_process = options.nblocks_per_sample,
        blocksize = options.blocksize,
        profile = options.profile,
        profile_out_path = "profile.txt",
    )
    return process.run(datasets, sequence)

def redraw(sequence, datasets, options):
    return [
        collector.reload(options.outdir)
        for (reader, collector) in sequence
        if hasattr(collector, "reload")
    ]

def parallel_draw(jobs, options):
    if len(jobs)==0:
        return
    jobs = [job for subjobs in jobs for job in subjobs]
    jobs = [jobs[i:i+len(jobs)/100]
            for i in xrange(0, len(jobs), len(jobs)/100+1)]

    parallel = build_parallel(
        parallel_mode = options.mode,
        quiet = options.quiet,
        processes = options.ncores,
    )
    parallel.begin()
    try:
        parallel.communicationChannel.put_multiple([{
            'task': grouped_run,
            'args': args,
            'kwargs': {},
        } for args in jobs])
        parallel.communicationChannel.receive()
    except KeyboardInterrupt:
        parallel.terminate()
    parallel.end()

if __name__ == "__main__":
    options = parse_args()

    sequence = build_sequence(options.sequence_cfg)
    datasets = get_datasets(options.dataset_cfg)
    if options.sample is not None:
        datasets = [d for d in datasets
                    if d.name==options.sample or \
                       d.parent==options.sample]

    if options.redraw:
        jobs = redraw(sequence, datasets, options)
    else:
        jobs = run(sequence, datasets, options)
    parallel_draw(jobs, options)
