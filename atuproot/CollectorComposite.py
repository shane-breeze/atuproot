from tqdm.auto import tqdm
from alphatwirl.datasetloop import CollectorComposite
from atpbar import disable
disable()

class CustomCollectorComposite(CollectorComposite):
    def collect(self, dataset_readers_list):
        ret = []
        for i, collector in enumerate(tqdm(
            self.components, desc="collecting results",
        )):
            ret.append(collector.collect([
                (dataset, tuple(r.readers[i] for r in readerComposites if hasattr(r, "readers")))
                for dataset, readerComposites in dataset_readers_list
            ]))
        return ret
