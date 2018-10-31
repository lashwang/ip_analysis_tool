#!/usr/bin/python
# -*- coding: utf-8 -*-
import fire
import re
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter


LOGCAT_DEFAULT_PATH = "/Users/simon/work/svn/dev_oc/engineering/projects/oc_client/dev/adclear_4_0/logcat.log"

def parse_file(fname):

    if not fname:
        fname = LOGCAT_DEFAULT_PATH

    dest_filename = fname + ".xlsx";

    with open(fname) as f:
        content = f.readlines()

    for line in content:
        pass


def main():
    fire.Fire(parse_file)
    pass


if __name__ == "__main__":
    main()
