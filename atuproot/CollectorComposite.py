import alphatwirl

from alphatwirl.loop import CollectorComposite
from alphatwirl.progressbar import ProgressReport

class CustomCollectorComposite(CollectorComposite):
    def collect(self, dataset_readers_list):
        ret = []
        for i, collector in enumerate(self.components):
            report = ProgressReport(name='collecting results', done=(i + 1), total=len(self.components))
            alphatwirl.progressbar.report_progress(report)

            ret.append(collector.collect([
                (dataset, tuple(r.readers[i] for r in readerComposites if hasattr(r, "readers")))
                for dataset, readerComposites in dataset_readers_list
            ]))
        return ret
