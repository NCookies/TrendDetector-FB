# -*- coding: utf-8 -*-

import argparse
import unicodecsv as csv
import sys


def commandline_arg(byte_string):
    unicode_string = byte_string.decode(sys.getfilesystemencoding())
    return unicode_string

parser = argparse.ArgumentParser()
parser.add_argument("-i", dest="input_file_name", default=None,
                    help="input file name(s) for CSV data to get data")
parser.add_argument("-target", dest="target_name", default=None,
                    type=commandline_arg,
                    help="target name is data for parsing")
parser.add_argument("-o", dest="output_file_name", default="data_set.csv",
                    type=commandline_arg)

args = parser.parse_args()

with open('input_data_set.csv', 'r') as r:
    reader = csv.reader(r)  # Here your csv file
    lines = [l for l in reader if unicode(l[3]) == unicode(args.target_name)]

    with open(args.output_file_name, 'wb') as w:
        writer = csv.writer(w)
        writer.writerows(lines)
