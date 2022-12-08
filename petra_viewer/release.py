__all__ = ("Release",)

__docformat__ = "restructuredtext"


class Release:
    """Summarize release information as class attributes.

    Release information:
        - name: (str) package name
        - version_info: (tuple<int,int,int,str,int>) The five components
          of the version number: major, minor, micro, releaselevel, and
          serial.
        - version: (str) package version in format <major>.<minor>.<micro>
        - release: (str) pre-release, post-release or development release;
          it is empty for final releases.
        - version_long: (str) package version in format
          <major>.<minor>.<micro><releaselevel><serial>
        - version_description: (str) short description for the current
          version
        - version_number: (int) <major>*100 + <minor>*10 + <micro>
        - description : (str) package description
        - long_description: (str) longer package description
        - authors: (dict<str(last name), tuple<str(full name),str(email)>>)
          package authors
        - url: (str) package url
        - download_url: (str) package download url
        - platform: (seq<str>) list of available platforms
        - keywords: (seq<str>) list of keywords
        - license: (str) the license
    """
    name = 'petra_viewer'
    version_info = (1, 4, 3)
    version = '.'.join(map(str, version_info[:3]))
    release = ''.join(map(str, version_info[3:]))
    separator = '.' if 'dev' in release or 'post' in release else ''
    version_long = version + separator + release

    version_number = int(version.replace('.', ''))
    description = 'Simple viewer of data, acquired by xray-detectors at PETRA3'
    long_description = description + '\nDetailed instruction can be found here: https://confluence.desy.de/display/FSP23/Data+viewer'

    license = 'GPL3'
    authors = (('Yury Matveev', 'yury.matveev@desy.de'),
               ('Mikhail Karnevskiy', 'mikhail.karnevskiy@desy.de'))
    author_lines = "\n".join([f"{name}: {email}" for name, email in authors])
    url = 'https://github.com/yamedvedya/data_viewer'
    download_url = 'https://pypi.org/project/petra-viewer/'
    platform = ['Linux', 'Windows XP/Vista/7/8/10']
