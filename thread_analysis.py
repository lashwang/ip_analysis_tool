#!/usr/bin/python
# -*- coding: utf-8 -*-
import fire
import re
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter
from abc import ABCMeta, abstractmethod




LOGCAT_DEFAULT_PATH = "/Users/simon/work/svn/dev_oc/engineering/projects/oc_client/dev/adclear_4_0/logcat.log"


class LogParserBase():
    __metaclass__ = ABCMeta

    def __init__(self):
        self.is_java = False



    @staticmethod
    def parse_line(line):
        log_parser = LogParserBase()


        if "[Native]" in line:
            log_parser.is_java = True
        elif "[JAVA]" in line:
            log_parser.is_java = False
        else:
            return None


        return log_parser


def parse_file(fname=None):

    if not fname:
        fname = LOGCAT_DEFAULT_PATH

    output_filename = fname + ".xlsx";

    with open(fname) as f:
        content = f.readlines()

    for line in content:
        log_parser = LogParserBase.parse_line(line)
        print log_parser
        pass


def main():
    fire.Fire(parse_file)
    pass


if __name__ == "__main__":
    main()
