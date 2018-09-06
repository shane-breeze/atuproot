import warnings
warnings.filterwarnings('ignore')

import argparse
import gzip
import pickle
import pprint

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Input path")
    return parser.parse_args()

if __name__ == "__main__":
    options = parse_args()

    path = options.input
    with gzip.open(path, 'rb') as f:
        package = pickle.load(f)
    print(package)

    print("TaskPackage(")
    print("\tname = {}".format(package.task.progressbar_label))
    print("\tinputPaths = {}".format(package.task.build_events.config.inputPaths))
    print(")")
