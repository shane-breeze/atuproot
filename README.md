# atuproot

Mainly use [alphatwirl](https://github.com/alphatwirl/alphatwirl),
[numpy](https://www.numpy.org/), [uproot](https://github.com/scikit-hep/uproot)
and [numba](https://numba.pydata.org/) to process [ROOT](https://root.cern.ch/)
`TTrees` for data analysis.

## How to use

Setup requires: alphatwirl, numpy, uproot, numba, pandas, pyyaml

The code uses input files located at Imperial. Currently can't chain multiple
files together. Run the code like so:

```
python run.py --data MET --blocksize 500000 --ncores 4
```

to run over the MET dataset (and associated MC samples) loading in 500k events
at a time into numpy arrays over 4 cores. You might need to reduce the
blocksize depending on memory use.
