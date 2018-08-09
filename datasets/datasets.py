import yaml
import os
from atuproot.Dataset import Dataset

def get_datasets(path="atuproot/datasets/datasets.yaml"):
    with open(path, 'r') as f:
        datasets_dict = yaml.load(f)

    datasets = []
    path = datasets_dict["path"]
    for dataset in datasets_dict["datasets"]:
        infopath = path.format(dataset)
        with open(infopath, 'r') as f:
            info = yaml.load(f)

        datasets.append(Dataset(
            name = dataset,
            parent = info["parent"],
            isdata = info["isdata"],
            xsection = info["xsection"],
            sumweights = info["sumweights"],
            lumi = datasets_dict["lumi"],
            energy = datasets_dict["energy"],
            files = info["files"],
            associates = [],
        ))

    # Associate samples
    not_extensions = [dataset
                      for dataset in datasets
                      if "_ext" not in dataset.name]
    for not_extension in not_extensions:
        associated_datasets = [dataset
                               for dataset in datasets
                               if not_extension.name in dataset.name]
        for dataset in associated_datasets:
            dataset.associates = associated_datasets

    return datasets

if __name__ == "__main__":
    datasets = get_datasets()
    print sorted(set([d.parent for d in datasets]))
