from __future__ import print_function
import yaml
import os
import six
import logging
from atuproot.Dataset import Dataset

def get_datasets(path):
    with open(path, 'r') as f:
        datasets_dict = yaml.load(f)

    datasets = []
    dataset_info_path = datasets_dict["path"]
    default = datasets_dict["default"]
    for dataset in set(datasets_dict["datasets"]):
        if isinstance(dataset, six.string_types):
            dataset_kwargs = _from_string(dataset, dataset_info_path, default)
        elif isinstance(dataset, dict):
            dataset_kwargs = _from_dict(dataset, dataset_info_path, default)
        else:
            raise TypeError("{} not a string or dict".format(dataset))
        datasets.append(Dataset(**dataset_kwargs))

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

def _from_string(dataset, path, default):
    cfg = default.copy()
    cfg["name"] = dataset
    return _extend_info(cfg, dataset, path)


def _from_dict(dataset, path, default):
    cfg = default.copy()
    cfg.update(dataset)
    if "name" not in cfg:
        raise RuntimeError("Dataset provided as dict, without key-value pair for 'name'")
    return _extend_info(cfg, dataset["name"], path)


def _extend_info(cfg, name, path):
    infopath = path.format(name)
    try:
        with open(infopath, 'r') as f:
            info = yaml.load(f)
            if info["name"] != cfg["name"]:
                raise ValueError("Mismatch between expected and read names: "
                                 "{} and {}".format(cfg["name"], info["name"]))
            cfg.update(info)
    except IOError:
        logger = logging.getLogger(__name__)
        logger.warning("IOError: {}".format(infopath))

    return cfg


if __name__ == "__main__":
    datas = get_datasets("datasets/cms_public_test.yaml")
    for d in datas:
        print(d)
