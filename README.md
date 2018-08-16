# atuproot

Mainly use [alphatwirl](https://github.com/alphatwirl/alphatwirl),
[numpy](https://www.numpy.org/), [uproot](https://github.com/scikit-hep/uproot)
and [numba](https://numba.pydata.org/) to process [ROOT](https://root.cern.ch/)
`TTrees` for data analysis.

## How to use

Can be installed using pip:
```
pip install --user git@github.com:benkrikler/atuproot.git
```

or for developing:
```
git clone git@github.com:benkrikler/atuproot.git
cd atuproot
pip install --user -e .
```

Pip should take care of the requirements, such as alphatwirl, numpy, uproot, numba, pandas, pyyaml

The code uses input files located at Imperial. Currently can't chain multiple
files together. Run the code like so:

```
python run_atuproot.py --blocksize 100000 --ncores 4
```

to run over the MET dataset (and associated MC samples) loading in 100k events
at a time into numpy arrays over 4 cores. You might need to reduce the
blocksize depending on memory use.
