#!/usr/bin/python3
import os
import runpy

from setuptools import setup, find_packages

REQUIRES_PYTHON = '>=3.7'

REQUIRED = [
    'pyqt5', 'attrs', 'pyqtgraph >= 0.11', 'psutil', 'pyshortcuts', 'numpy', 'scipy', 'h5py >= 2.5', 'python-dateutil'
]

EXTRA_REQUIRED = {'ASAPO': ['hdf5plugin'],
                  'CONVERTER': ['xrayutilities'],
                  'SILX': ['silx'],
                  '3D': ['PyOpenGL']
                  }

def abspath(*path):
    """A method to determine absolute path for a given relative path to the
    directory where this setup.py script is located"""
    setup_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(setup_dir, *path)

def get_release_info():
    namespace = runpy.run_path(abspath("petra_viewer/release.py"), run_name="petra_viewer.release")
    return namespace["Release"]

Release = get_release_info()

# Where the magic happens:
setup(
    name=Release.name,
    version=Release.version_long,
    description=Release.description,
    long_description=Release.long_description,
    long_description_content_type='text/markdown',
    author=Release.authors[0][0],
    author_email=Release.authors[0][1],
    download_url=Release.download_url,
    platforms=Release.platform,
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(),
    package_dir={'petra_viewer': 'petra_viewer',},
    package_data={'petra_viewer': ['README.txt', 'LICENSE.txt',
                                   'petra_viewer/*.py', 'petra_viewer/*.ini', 'petra_viewer/*.desktop'],},
    install_requires=REQUIRED,
    extras_require=EXTRA_REQUIRED,
    include_package_data=True,
    license='GPLv3',
    entry_points={'console_scripts': ['petra_viewer = petra_viewer:main',],},
    scripts=['petra_viewer/petra_viewer.sh'],
    data_files=[('share/applications', ['petra_viewer/petra_viewer.desktop'])],
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Development Status :: 3 - Alpha'
    ],
)