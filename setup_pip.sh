#!/bin/bash

# Shamelessly taken from the FAST-RA1 project
cvmfs_PythonDir=/cvmfs/sft.cern.ch/lcg/releases/Python/2.7.13-597a5/x86_64-slc6-gcc62-opt/
cvmfs_PipDir=/cvmfs/sft.cern.ch/lcg/releases/pip/8.1.2-c9f5a/x86_64-slc6-gcc62-opt/
cvmfs_GCCSetup=/cvmfs/sft.cern.ch/lcg/contrib/gcc/6.2/x86_64-slc6/setup.sh
cvmfs_RootSetup=/cvmfs/sft.cern.ch/lcg/releases/LCG_88/ROOT/6.08.06/x86_64-slc6-gcc62-opt/bin/thisroot.sh
cvmfs_Libs=/cvmfs/sft.cern.ch/lcg/views/LCG_88/x86_64-slc6-gcc62-opt/
cvmfs_LzmaDir=/cvmfs/cms.cern.ch/slc6_amd64_gcc620/external/xz/5.2.2/

if [ -z "$(which root-config 2>/dev/null)" ] \
    || [[ "$(root-config --version)" != 6.* ]] ;then
    if [ -r "${cvmfs_RootSetup}" ] && [ -r "$cvmfs_GCCSetup" ]; then
      source "${cvmfs_GCCSetup}"
      source "${cvmfs_RootSetup}"
    else
      echo "Cannot setup ROOT 6 and it doesn't seem to be configured already, this might be an issue..."
    fi
fi

top_dir(){
  local Canonicalize="readlink -f"
  $Canonicalize asdf &> /dev/null || Canonicalize=realpath
  dirname "$($Canonicalize "${BASH_SOURCE[0]}")"
}

export ROOT_DIR="$(top_dir)"
export EXTERNALS_DIR="$(top_dir)/externals"

build_some_path(){
  local NewPath="$1" ;shift
  for dir in "$@";do
    if ! $( echo "$NewPath" | grep -q '\(.*:\|^\)'"$dir"'\(:.*\|$\)' ); then
      NewPath="${dir}${NewPath:+:${NewPath}}"
    fi
  done
  echo "$NewPath"
}

build_path(){
  local Dirs=( "${ROOT_DIR}"/bin "${EXTERNALS_DIR}"/pip/bin )
  Dirs+=( {"$cvmfs_PythonDir","$cvmfs_PipDir"}/bin)
  build_some_path "$PATH" "${Dirs[@]}"
}

build_python_path(){
  local Dirs=( "${ROOT_DIR}" "${EXTERNALS_DIR}"/pip/lib/python2.7/site-packages )
  Dirs+=( {"$cvmfs_PythonDir","$cvmfs_PipDir"}/lib/python2.7/site-packages/)

  build_some_path "$PYTHONPATH" "${Dirs[@]}"
}

export PYTHONPATH="$(build_python_path)"
export PATH="$(build_path)"

export LD_LIBRARY_PATH="$(build_some_path "$LD_LIBRARY_PATH" "${cvmfs_Libs}"{lib,lib64} )"

# Special treatment needed for setuptools
python -m pip install --prefix "${EXTERNALS_DIR}"/pip -U setuptools --ignore-installed
python -m pip install --prefix "${EXTERNALS_DIR}"/pip -r requirements.txt --ignore-installed
python -m pip install --prefix "${EXTERNALS_DIR}"/pip backports.lzma --ignore-installed --global-option=build_ext --global-option="-L${cvmfs_LzmaDir}/lib/" --global-option="-I${cvmfs_LzmaDir}/include/"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}":"${cvmfs_LzmaDir}"/lib

unset build_some_path
unset build_path
unset build_python_path
unset cvmfs_PythonDir
unset cvmfs_PipDir
unset cvmfs_GCCSetup
unset cvmfs_RootSetup
unset cvmfs_LzmaDir
