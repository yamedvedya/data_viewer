from optparse import OptionParser


def get_options(args=None):
    parser = OptionParser()

    parser.add_option("-d", "--dir", dest="dir", help="start folder")

    parser.add_option("-f", "--file", dest="file", help="open file after start")

    parser.add_option("--asapo", action='store_true', dest='asapo', help="include ASAPO scan")
    parser.add_option("--sardana", action='store_true', dest='sardana', help="include Sardana scan")
    parser.add_option("--beam", action='store_true', dest='beam', help="include Beamline view")
    parser.add_option("--tests", action='store_true', dest='tests', help="include Tests Datasets")

    parser.add_option("--log", action='store_true', dest='log', help="include ASAPO scan")

    (options, _) = parser.parse_args(args)

    return options