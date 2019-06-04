import tqdm
import copy

from alphatwirl.datasetloop import DatasetReaderComposite, DatasetLoop
from alphatwirl.loop import EventLoopRunner, DatasetIntoEventBuildersSplitter

from .EventBuilderConfigMaker import EventBuilderConfigMaker
from .EventBuilder import EventBuilder
from .ReaderComposite import CustomReaderComposite as ReaderComposite
from .CollectorComposite import CustomCollectorComposite as CollectorComposite
from .EventDatasetReader import CustomEventDatasetReader as EventDatasetReader

import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class AtUproot(object):
    def __init__(
        self, outdir, quiet=False, parallel_mode='multiprocessing',
        process=4, sge_opts="-q hep.q", max_blocks_per_dataset=-1,
        max_blocks_per_process=-1, max_files_per_dataset=-1,
        max_files_per_process=1, nevents_per_block=1000000, branch_cache={},
    ):
        self.parallel_mode = parallel_mode
        self.sge_opts = sge_opts
        self.ncores = process
        self.quiet = quiet

        self.outdir = outdir
        self.max_blocks_per_dataset = max_blocks_per_dataset
        self.max_blocks_per_process = max_blocks_per_process
        self.max_files_per_dataset = max_files_per_dataset
        self.max_files_per_process = max_files_per_process
        self.nevents_per_block = nevents_per_block
        self.branch_cache = branch_cache

    def run(self, datasets, reader_collector_pairs):
        loop = self._configure(datasets, reader_collector_pairs)

        event_loops = []
        for d in tqdm.tqdm(
            loop.datasets, unit='dataset', dynamic_ncols=True,
            disable=self.quiet,
        ):
            for r in loop.reader.readers:
                r.begin()

            for r in loop.reader.readers:
                for b in r.split_into_build_events(d):
                    r_copy = copy.deepcopy(r.reader)
                    event_loop = r.EventLoop(b, r_copy, d.name)
                    event_loops.append(event_loop)

            for r in loop.reader.readers:
                r.end()

        tasks = [
            {"task": event_loop, "args": [], "kwargs": {}}
            for event_loop in event_loops
        ]

        return tasks

        if self.parallel_mode=="multiprocessing" and self.ncores==0:
            results = pysge.local_submit(tasks)
        elif self.parallel_mode=="multiprocessing":
            results = pysge.mp_submit(tasks, ncores=self.ncores)
        elif self.parallel_mode=="sge":
            results = pysge.sge_submit(
                    "zinv", "_ccsp_temp/", tasks=tasks,
                options=self.sge_opts, sleep=5,
                request_resubmission_options=True,
            )
        return results

    def _treename_of_files(self, datasets):
        return {
            path: dataset.tree
            for dataset in datasets
            for path in dataset.files
        }

    def _configure(self, datasets, reader_collector_pairs):
        dataset_readers = DatasetReaderComposite()

        reader_top = ReaderComposite()
        collector_top = CollectorComposite()
        for r, c in reader_collector_pairs:
            reader_top.add(r)
            collector_top.add(c)
        eventLoopRunner = EventLoopRunner()
        eventBuilderConfigMaker = EventBuilderConfigMaker(
            self.nevents_per_block,
            treename_of_files_map = self._treename_of_files(datasets),
            branch_cache = self.branch_cache,
        )
        datasetIntoEventBuildersSplitter = DatasetIntoEventBuildersSplitter(
            EventBuilder = EventBuilder,
            eventBuilderConfigMaker = eventBuilderConfigMaker,
            maxEvents = self.max_blocks_per_dataset,
            maxEventsPerRun = self.max_blocks_per_process,
            maxFiles = self.max_files_per_dataset,
            maxFilesPerRun = self.max_files_per_process,
        )
        eventReader = EventDatasetReader(
            eventLoopRunner = eventLoopRunner,
            reader = reader_top,
            collector = collector_top,
            split_into_build_events = datasetIntoEventBuildersSplitter
        )

        dataset_readers.add(eventReader)
        return DatasetLoop(datasets=datasets, reader=dataset_readers)
