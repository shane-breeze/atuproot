# atuproot

Mainly use [alphatwirl](https://github.com/alphatwirl/alphatwirl),
[numpy](https://www.numpy.org/), [uproot](https://github.com/scikit-hep/uproot)
and [numba](https://numba.pydata.org/) to process [ROOT](https://root.cern.ch/)
`TTrees` for data analysis.

## How to use

Can be installed using pip:
```
pip install --user git@github.com:shane-breeze/atuproot.git
```

or for developing:
```
git clone git@github.com:shane-breeze/atuproot.git
cd atuproot
pip install --user -e .
```

Pip should take care of the requirements, such as alphatwirl, numpy, uproot, numba, pandas, pyyaml

The script `run_atuproot.py` is an example of how to use the atuproot interface
to run over ROOT trees. Run the code like so:

```
python run_atuproot.py ${SEQUENCE_CFG} ${DATASET_CFG} --blocksize 100000 --ncores 4
```

where `${SEQUENCE_CFG}` and `${DATASET_CFG}` are paths to config files to setup
the sequence to run and datasets to process. This will then load 100k events
at a time into numpy arrays over 4 cores. You might need to reduce the
blocksize depending on memory use.

## Binder tutorial

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/shane-breeze/atuproot/alphatwirl-adaptors?filepath=binder%2Ftutorial.ipynb)
