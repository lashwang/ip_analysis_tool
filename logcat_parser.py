#!/usr/bin/python
# -*- coding: utf-8 -*-
import fire
import re



def parser_line(line):

    if "[Native]" not in line:
        return

    line = line.strip()

    # '06-08 14:51:13.418 22651 22786 V [Native]proxy: 06-08 14:51:13.418 +0800 22786 [FT] [ProcessorInterface.cpp:111] (0) - CSM [00068001] in_eof_process CMT_EOF process started'

    compiled_pattern = re.compile(r'(\s+)CSM(\s*)\[(\S+)\]')

    matchObj = compiled_pattern.match(line)

    if matchObj:
        print line


    pass


def parse_file(fname):
    with open(fname) as f:
        content = f.readlines()

    for line in content:
        parser_line(line)

    pass


def main():
    fire.Fire(parse_file)
    pass


if __name__ == "__main__":
    main()
