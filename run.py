from alphatwirl.loop import NullCollector
from atuproot.AtUproot import AtUproot

from sequence.sequence import sequence
from datasets.datasets import datasets

import logging
logging.getLogger("ROOT.TClass.Init").setLevel(logging.ERROR)

from rootpy import log
log_mpl = log["/matplotlib"]
log_mpl.setLevel(log_mpl.INFO)

logger = log["/"+__name__]
logger.setLevel(log.INFO)

if __name__ == "__main__":
    process = AtUproot("temp",
        quiet = False,
        parallel_mode = 'multiprocessing',
        process = 0,
        max_events_per_process = -1,
        profile = False,
        profile_out_path = None,
    )
    process.run(datasets, [(module, NullCollector()) for module in sequence])
