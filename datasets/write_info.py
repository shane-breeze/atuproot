from __future__ import print_function
import yaml
import os
from xsection import xsdict
from datasets import datasets_dict

input_path = "/vols/cms/ZinvWidth/NanoAOD/201806_Jun/data/{}/info.yaml"
for parent, names in datasets_dict.items():
    for name in names:
        print(name)
        info = yaml.load(open(input_path.format(name), 'r'))
        if "Run2016" in name:
            info["isdata"] = True
            info["xsection"] = None
        else:
            info["isdata"] = False
            info["xsection"] = xsdict[name]

        info["files"] = [os.path.abspath(input_path.format(name).replace("info.yaml", "")+f)
                         for f in info["files"]]
        info["parent"] = parent

        yaml.dump(info, open(input_path.format(name), 'w'))

