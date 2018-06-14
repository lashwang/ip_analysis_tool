#!/usr/bin/python
# -*- coding: utf-8 -*-
import fire
import re

def parser_line(line):

    if "[Native]" not in line:
        return


    matchObj = re.match(r'(\s+)CSM(\s*)\[(\S+)\]',line)

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
