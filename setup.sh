# Created by matveyev at 07.04.2021

BASEDIR=`dirname $0`
cd $BASEDIR || exit

export VIEWERPATH=$PWD/
export PYTHONPATH=$PYTHONPATH:$VIEWERPATH

python3 ./build.py
python3 ./make_alias.py
chmod +x start_online_editor.sh

python3 -m venv --system-site-packages ./venv
. venv/bin/activate

wget http://nims.desy.de/extra/asapo/linux_packages/debian10.7/asapo_consumer-21.03.0.tar.gz
pip3 install asapo_consumer-21.03.0.tar.gz

