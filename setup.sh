#!/bin/bash
cvmfs_pythondir=/cvmfs/sft.cern.ch/lcg/releases/Python/2.7.13-b163d/x86_64-slc6-gcc62-opt/
cvmfs_pipdir=/cvmfs/sft.cern.ch/lcg/releases/pip/9.0.1-54273/x86_64-slc6-gcc62-opt/
cvmfs_gccsetup=/cvmfs/sft.cern.ch/lcg/contrib/gcc/6.2/x86_64-slc6/setup.sh
cvmfs_rootsetup=/cvmfs/sft.cern.ch/lcg/releases/LCG_88/ROOT/6.08.06/x86_64-slc6-gcc62-opt/bin/thisroot.sh
lzma_path=/cvmfs/cms.cern.ch/slc6_amd64_gcc620/external/xz/5.2.2/

# Setup ROOT
if [ -z "$(which root-config 2>/dev/null)" ] \
    || [[ "$(root-config --version)" != 6.* ]]; then
    if [ -r "${cvmfs_rootsetup}" ] && [ -r "$cvmfs_gccsetup" ]; then
        source "${cvmfs_gccsetup}"
        source "${cvmfs_rootsetup}"
    else
        echo "Cannot setup ROOT 6 and it doesn't seem to be setup already"
    fi
fi

top_dir(){
    local Canonicalize="readlink -f"
    $Canonicalize asdf &> /dev/null || Canonicalize=realpath
    dirname "$($Canonicalize "${BASH_SOURCE[0]}")"
}

export TOPDIR="$(top_dir)"
export EXTERNALS="$(top_dir)/externals"

build_some_path(){
    local new_path="$1"; shift
    for dir in "$@"; do
        if ! $( echo "$new_path" | grep -q '\(.*:\|^\)'"$dir"'\(:.*\|$\)' ); then
            new_path="${dir}${new_path:+:${new_path}}"
        fi
    done
    echo "$new_path"
}

build_path(){
    local Dirs=( "${EXTERNALS}"/pip/bin )
    Dirs+=( {"$cvmfs_pythondir","$cvmfs_pipdir"}/bin )
    build_some_path "$PATH" "${Dirs[@]}"
}

build_python_path(){
    local Dirs=( "${TOPDIR}" "${EXTERNALS}"/pip/lib/python2.7/site-packages )
    Dirs+=( "${TOPDIR}"/atuproot )
    Dirs+=( {"$cvmfs_pythondir","$cvmfs_pipdir"}/lib/python2.7/site-packages/)

    build_some_path "$PYTHONPATH" "${Dirs[@]}"
}

export PYTHONPATH="$(build_python_path)"
export PATH="$(build_path)"

python -m pip install --prefix "${EXTERNALS}"/pip -U setuptools --disable-pip-version-check
python -m pip install --prefix "${EXTERNALS}"/pip -r requirements.txt --disable-pip-version-check
python -m pip install --prefix ${EXTERNALS}/pip backports.lzma --global-option=build_ext --global-option="-L${lzma_path}/lib/" --global-option="-I${lzma_path}/include/"
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${lzma_path}/lib

unset build_some_path
unset build_path
unset build_python_path
unset cvmfs_pythondir
unset cvmfs_pipdir
unset lzma_path
