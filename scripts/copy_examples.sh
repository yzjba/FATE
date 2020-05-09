#!/usr/bin/env bash

exmaples_package=$(python -c 'import examples; print(examples.__file__)')
dir_path=$(dirname "$exmaples_package")
echo "coping $dir_path to $1"
cp -r "$dir_path" "$1"
echo "done"
