#!/usr/bin/python
# -*- coding: utf-8 -*-
import fire
import re
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter

wb = Workbook()
dest_filename = 'logcat_output.xlsx'
ws_csm = wb.active
ws_csm.title = "csm"
ws_netlog = wb.create_sheet(title="netlog")

NET_LOG_HEADERS_V15 = ['timestamp', 'clientAddress', 'logType', 'formatVersion', \
                       'clientBytesIn', 'clientBytesOut', 'serverBytesIn', 'serverBytesOut', \
                       'cacheBytesIn', 'cacheBytesOut', 'host', 'application', 'applicationStatus', \
                       'operation', 'protocolStack', 'networkProtocolStack', 'networkInterface', \
 \
                       'responseDelay', 'responseDuration', 'requestId', 'subscriptionId', 'statusCode', \
                       'errorCode', 'contentType', 'headerLength', 'contentLength', 'responseHash', \
 \
                       'analysisString', 'analysis', 'optimization', 'protocolDetection', 'destinationIp',
                       'destinationPort', \
                       'redirectedToIp', 'redirectedToPort', 'sequenceNumber', 'requestDelay', 'radioAwarenessStatus', \
                       'originatorId', 'csmCreationTime', 'clientSrcPort', 'cspSrcPort'
                       ]


CSM_LOG_HEADER = ['date', 'time', 'tid', 'csm', 'filename', 'flie_line', 'errcode', 'log']

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
        ws_csm.append([date, time, tid, csm, filename, flie_line, errcode, log])

    reg_str = r"NetLog\s+\(.*\):\s+(.*)"
    matchObj = re.search(reg_str, line)
    if matchObj:
        netlog_str = matchObj.group(1)
        ws_netlog.append(netlog_str.split(','))


    pass


def parse_file(fname):
    with open(fname) as f:
        content = f.readlines()


    ws_csm.append(CSM_LOG_HEADER)
    ws_netlog.append(NET_LOG_HEADERS_V15)
    for line in content:
        try:
            parser_line(line)
        except Exception:
            print "error:" + line

    wb.save(filename=dest_filename)

    pass


def main():
    fire.Fire(parse_file)
    pass


if __name__ == "__main__":
    main()
