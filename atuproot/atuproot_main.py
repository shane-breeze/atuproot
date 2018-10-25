from alphatwirl.parallel import build_parallel
from alphatwirl.datasetloop import (DatasetReaderComposite, ResumableDatasetLoop,
                                    DatasetLoop)
from alphatwirl.loop import (ReaderComposite, CollectorComposite,
                             MPEventLoopRunner, DatasetIntoEventBuildersSplitter,
                             EventDatasetReader)
from alphatwirl.misc import print_profile_func

from .EventBuilderConfigMaker import EventBuilderConfigMaker
from .EventBuilder import EventBuilder

import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class AtUproot(object):
    def __init__(self, outdir,
                 force=False, quiet=False,
                 parallel_mode='multiprocessing',
                 dispatcher_options = dict(),
                 process = 4,
                 user_modules = (),
                 max_blocks_per_dataset = -1,
                 max_blocks_per_process = -1,
                 max_files_per_dataset = -1,
                 max_files_per_process = 1,
                 nevents_per_block = 1000000,
                 profile = False, profile_out_path = None
    ):
        self.parallel = build_parallel(
            parallel_mode = parallel_mode,
            quiet = quiet,
            processes = process,
            user_modules = user_modules,
            dispatcher_options = dispatcher_options
        )
        self.outdir = outdir
        self.force = force
        self.max_blocks_per_dataset = max_blocks_per_dataset
        self.max_blocks_per_process = max_blocks_per_process
        self.max_files_per_dataset = max_files_per_dataset
        self.max_files_per_process = max_files_per_process
        self.nevents_per_block = nevents_per_block
        self.profile = profile
        self.profile_out_path = profile_out_path
        self.parallel_mode = parallel_mode

    def run(self, datasets, reader_collector_pairs):
        self.parallel.begin()
        try:
            loop = self._configure(datasets, reader_collector_pairs)
            return self._run(loop)
        except KeyboardInterrupt:
            logger = logging.getLogger(__name__)
            logger.warning('received KeyboardInterrupt')
            logger.warning('terminating running jobs')
            self.parallel.terminate()
        self.parallel.end()

    def _treename_of_files(self, datasets):
        return {path: dataset.tree
                for dataset in datasets
                for path in dataset.files}

    def _configure(self, datasets, reader_collector_pairs):
        dataset_readers = DatasetReaderComposite()

        reader_top = ReaderComposite()
        collector_top = CollectorComposite()
        for r, c in reader_collector_pairs:
            reader_top.add(r)
            collector_top.add(c)
        eventLoopRunner = MPEventLoopRunner(
            self.parallel.communicationChannel
        )
        eventBuilderConfigMaker = EventBuilderConfigMaker(
            self.nevents_per_block,
            treename_of_files_map = self._treename_of_files(datasets),
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

        if self.parallel_mode not in ('multiprocessing',):
            loop = ResumableDatasetLoop(
                datasets=datasets, reader=dataset_readers,
                workingarea=self.parallel.workingarea
            )
        else:
            loop = DatasetLoop(
                datasets=datasets,
                reader=dataset_readers
            )

        return loop

    def _run(self, loop):
        if not self.profile:
            result = loop()
        else:
            result = print_profile_func(
               func=loop,
               profile_out_path=self.profile_out_path
            )
        return result
