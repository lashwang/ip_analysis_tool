#!/usr/bin/python
# -*- coding: utf-8 -*-

import commands
import sys


gMonitorThreads = [".adclear:engine","n.adclear:proxy"]



def main():
    check_device()
    psAdclear = read_process_for_adclear()
    for pid in psAdclear:
        read_task_info(int(pid))
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


def read_task_info(pid):
    cmd = "adb shell ls /proc/{}/task".format(pid)
    output = commands.getstatusoutput(cmd)
    if output[0] != 0:
        print "read sub task failed for pid {}".format(pid)
        return

    taskList = output[1].split("\n")
    for tid in taskList:
        tid = int(tid.strip())
        cmd = "adb shell cat /proc/{}/task/{}/stat".format(pid,tid)
        output = commands.getstatusoutput(cmd)
        if output[0] != 0:
            continue

        taskInfo = output[1].split()
        taskName = taskInfo[1]
        taskName = taskName[1:]
        taskName = taskName[:-1]

        if taskName in gMonitorThreads:
            if pid != tid:
                print taskInfo



if __name__ == "__main__":
    main()
