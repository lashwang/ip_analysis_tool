#!/usr/bin/python
# -*- coding: utf-8 -*-
import fire
import re
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter

wb = Workbook()
dest_filename = 'logcat_output.xlsx'
ws1 = wb.active
ws1.title = "csm"





def parser_line(line):

    if "[Native]" not in line:
        return

    line = line.strip()
    reg_str \
        = r"\[Native\]\S+\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\S+\s+\[(\S+):(\S+)\]\s+\((\S+)\)\s+-\s+CSM\s+\[(\S+)\]\s+(.*)"


    matchObj = re.search(reg_str,line)

    if matchObj:
        index = 1
        date = matchObj.group(index)
        index += 1
        time = matchObj.group(index)
        index += 1
        time_zone = matchObj.group(index)
        index += 1
        tid = matchObj.group(index)
        index += 1
        filename = matchObj.group(index)
        index += 1
        flie_line = matchObj.group(index)
        index += 1
        errcode = matchObj.group(index)
        index += 1
        csm = matchObj.group(index)
        index += 1
        log = matchObj.group(index)
        ws1.append([date,time,tid,csm,filename,flie_line,errcode,log])



    pass


def parse_file(fname):
    with open(fname) as f:
        content = f.readlines()

    for line in content:
        parser_line(line)

    wb.save(filename=dest_filename)

    pass


def main():
    fire.Fire(parse_file)
    pass


if __name__ == "__main__":
    main()
