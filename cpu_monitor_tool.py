#!/usr/bin/python
# -*- coding: utf-8 -*-

import commands
import sys


gMonitorThreads = [".adclear:engine","n.adclear:proxy"]



def main():
    check_device()
    psAdclear = read_process_for_adclear()
    for ps in psAdclear:

    pass




def check_device():
    errMsg = "No device connected,please check"
    output = commands.getstatusoutput('adb devices')
    error = False
    if output[0] != 0:
        sys.stderr.write(errMsg)
        error = True

    deviceInfo = output[1].split("\n")
    if deviceInfo[1] is "":
        sys.stderr.write(errMsg)
        error = True

    if error:
        exit(1)


def read_process_for_adclear():
    output = commands.getstatusoutput('adb shell ps')
    psAdclear = []
    if output[0] != 0:
        return psAdclear

    psList = output[1].split("\n")
    for line in psList:
        psInfo = line.split()
        if len(psInfo) == 9:
            appName = psInfo[8]
            if "adclear" in appName:
                if "engine" in appName or "proxy" in appName:
                    psAdclear.append(psInfo[1])


    return psAdclear



if __name__ == "__main__":
    main()
