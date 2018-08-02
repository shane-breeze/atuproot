#!/bin/bash
export PATH="~/miniconda2/bin:$PATH"
source activate atuproot

export PYTHONPATH=$PYTHONPATH:$PWD:$PWD/atuproot:$PWD/sequence
