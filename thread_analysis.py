#!/usr/bin/python
# -*- coding: utf-8 -*-
import fire
import re
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter
from abc import ABCMeta, abstractmethod




LOGCAT_DEFAULT_PATH = "/Users/simon/Downloads/Logcat_d5c50fd4106d8d14_2018-10-31-00.00.00_2018-11-01-00.00.00-r-00000"

log_all_list = []
log_thread_dic = {}



class LogParserBase():
    __metaclass__ = ABCMeta
    parer_function = None


    def __init__(self):
        self.is_java = False
        self.orig_line = None
        self.csm = None
        self.date = None
        self.time = None
        self.pid = None
        self.tid = None
        self.log = None
        self.filename = None
        self.fileline = None
        self.classname = None


    @staticmethod
    def get_filename_and_line():
        pass


    @staticmethod
    def parse_format_2(self):
        reg_str = r"^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+(\S+):\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(.*)"
        matchObj = re.search(reg_str, self.orig_line)
        lable = None
        if matchObj:
            self.date = matchObj.group(1)
            self.time = matchObj.group(2)
            self.pid = matchObj.group(3)
            self.tid = matchObj.group(4)
            lable = matchObj.group(5)
            self.log = matchObj.group(6)
        else:
            return False

        if not self.pid.isdigit():
            return False

        if not self.tid.isdigit():
            return False

        if not self.is_java:
            reg_str = "^\[(\S+):(\d+)\]\s+\((\S+)\)\s+\-\s+(.*)"
            matchObj = re.search(reg_str, self.log)
            if matchObj:
                self.filename = matchObj.group(1)
                self.fileline = matchObj.group(2)
                self.log = matchObj.group(4)
            else:
                return False

        if self.is_java:
            reg_str = "^\[\S*\](\S+)"
            matchObj = re.search(reg_str, self.log)
            if matchObj:
                self.classname = matchObj.group(1)
            else:
                return False


        return True

        pass

    @staticmethod
    def parse_format_1(self):
        reg_str = r"^\S+\((\S+)\):\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\[\S+\]\s+(.*)"
        matchObj = re.search(reg_str, self.orig_line)
        if matchObj:
            self.pid = matchObj.group(1)
            self.tid = matchObj.group(5)
        else:
            return False

        if not self.pid.isdigit():
            return False

        if not self.tid.isdigit():
            return False

        self.date = matchObj.group(2)
        self.time = matchObj.group(3)
        self.log = matchObj.group(6)

        if not self.is_java:
            reg_str = "^\[(\S+):(\d+)\]\s+\((\S+)\)\s+\-\s+(.*)"
            matchObj = re.search(reg_str, self.log)
            if matchObj:
                self.filename = matchObj.group(1)
                self.fileline = matchObj.group(2)
                self.log = matchObj.group(4)
            else:
                return False

        reg_str = r"(.*)\[([0-9a-fA-F]{8})\](.*)"
        matchObj = re.search(reg_str, self.log)
        if matchObj:
            self.csm = matchObj.group(2)
        else:
            self.csm = None

        return True




    @staticmethod
    def parse_line(line):
        log_parser = LogParserBase()


        if "[Native]" in line:
            log_parser.is_java = False
        elif "[JAVA]" in line:
            log_parser.is_java = True
        else:
            return None

        log_parser.orig_line = line


        if not LogParserBase.parer_function:
            if LogParserBase.parse_format_1(log_parser):
                LogParserBase.parer_function = LogParserBase.parse_format_1
            elif LogParserBase.parse_format_2(log_parser):
                LogParserBase.parer_function = LogParserBase.parse_format_2
        else:
            ret = LogParserBase.parer_function(log_parser)
            if not ret:
                #print "Unkown line:" + line
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
        if not log_parser:
            continue
        log_all_list.append(log_parser)


    print "process finished."


def main():
    fire.Fire(parse_file)
    pass


if __name__ == "__main__":
    main()
