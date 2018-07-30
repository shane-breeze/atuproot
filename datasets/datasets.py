import yaml
import os
from atuproot.Dataset import Dataset

def get_datasets(path="/vols/build/cms/sdb15/atuproot/datasets/datasets.yaml"):
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
            lumi = datasets_dict["lumi"],
            energy = datasets_dict["energy"],
            files = info["files"],
        ))
    return datasets
