#!/usr/bin/env bash
BASEDIR=`dirname $0`
cd $BASEDIR ||exit

export VIEWERPATH=$PWD/
export PYTHONPATH=$PYTHONPATH:$VIEWERPATH
./venv/bin/python ./data_viewer.py $1 --log