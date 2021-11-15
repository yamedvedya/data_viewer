from subprocess import check_output, STDOUT


def get_version():
    cmd = "git log -1 --format='%at' | xargs -I{} date -d @{} +'%Y/%m/%d %H:%M:%S'"
    version = check_output(cmd, stderr=STDOUT, shell=True, universal_newlines=True)
    version = version.replace("\n", "")
    return version


__version__ = get_version()
