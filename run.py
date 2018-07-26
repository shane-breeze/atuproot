from alphatwirl.loop import NullCollector
from atuproot.AtUproot import AtUproot
from atuproot.Dataset import Dataset

from sequence.sequence import sequence

import logging
logging.getLogger("ROOT.TClass.Init").setLevel(logging.ERROR)

from rootpy import log
log_mpl = log["/matplotlib"]
log_mpl.setLevel(log_mpl.INFO)

logger = log["/"+__name__]
logger.setLevel(log.INFO)

if __name__ == "__main__":
    dataset = Dataset(name="ZJetsToNuNu_Pt-250To400", files=[
        "/vols/build/cms/sdb15/atuproot/nanoAOD_1.root",
        "/vols/build/cms/sdb15/atuproot/nanoAOD_2.root",
    ])

    process = AtUproot("temp",
        quiet = False,
        parallel_mode = 'sge',
        process = 4,
        max_events_per_process = -1,
        profile = False,
        profile_out_path = None,
    )
    process.run([dataset], [(module, NullCollector()) for module in sequence])
