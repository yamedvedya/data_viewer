#!/usr/bin/env bash
# Created by matveyev at 07.04.2021

BASEDIR=`dirname $0`
cd $BASEDIR || exit

export VIEWERPATH=$PWD/
export PYTHONPATH=$PYTHONPATH:$VIEWERPATH

python3 ./build.py
python3 ./make_alias.py
chmod +x start_viewer.sh

cp ./sample_settings.ini ./settings.ini

{
  python3 -m venv --system-site-packages ./venv
} || {
pip install --user virtualenv
$HOME/.local/bin/virtualenv  -p python3 --system-site-packages venv
}
. venv/bin/activate

pip3 install --upgrade pip

wget http://nims.desy.de/extra/asapo/linux_packages/debian10.7/asapo_consumer-21.03.0.tar.gz
pip3 install asapo_consumer-21.03.0.tar.gz
rm ./asapo_consumer-21.03.0.tar.gz

pip3 install hdf5plugin
pip3 install scikit-image
pip3 install attrs
pip3 install pyqtgraph
pip3 install psutil
pip3 install xrayutilities