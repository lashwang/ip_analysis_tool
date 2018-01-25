#!/usr/bin/python
# -*- coding: utf-8 -*-

import fire
from zipfile import ZipFile, is_zipfile
import StringIO
import fileinput
import sys
import gzip
import binascii
import pandas





def is_gz_file(filepath):
    with open(filepath, 'rb') as test_f:
        return binascii.hexlify(test_f.read(2)) == b'1f8b'

def open_file_input_string(input_file):
    if is_gz_file(input_file):
        with gzip.open(input_file, 'rb') as f:
            file_content = f.read()
        file_object = StringIO.StringIO(file_content)
    else:
        file_object = fileinput.input(input_file)

    return file_object


def parse_from_file(f):
    global df_power,df_netlog
    file_object = open_file_input_string(f)
    df = pandas.read_csv(file_object,header=None,error_bad_lines=False)
    df_power = df[df.iloc[:, 4] == 'battery']

    return df

def default():
    parse_from_file('data/Crcs_fd544095-7116-4291-9f01-6f5cf67f607b_2018-01-03-00.00.00_2018-01-04-00.00.00-r-00000.gz')

class CRCSAnaLyser(object):
    def file(self,f):
        parse_from_file(f)

    def folder(self,d):
        pass



def main():
    if len(sys.argv) == 1:
        fire.Fire(default)
    else:
        fire.Fire(CRCSAnaLyser)




if __name__ == "__main__":
    main()