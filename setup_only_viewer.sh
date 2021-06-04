#!/usr/bin/env bash
# Created by matveyev at 07.04.2021

BASEDIR=`dirname $0`
cd $BASEDIR || exit

export VIEWERPATH=$PWD/
export PYTHONPATH=$PYTHONPATH:$VIEWERPATH

{
  python3 -m venv --system-site-packages ./venv
} || {
pip install --user virtualenv
$HOME/.local/bin/virtualenv  -p python3 --system-site-packages venv
}
. venv/bin/activate

pip3 install pyqtgraph
pip3 install psutil
pip3 install xrayutilities

python3 ./build.py
python3 ./make_alias.py
chmod +x start_viewer.sh

cp ./sample_settings.ini ./settings.ini