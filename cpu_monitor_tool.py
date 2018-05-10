#!/usr/bin/python
# -*- coding: utf-8 -*-

import commands
import sys
import datetime

#send-email
import smtplib
import time
import os
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders
from email.mime.application import MIMEApplication
from os.path import basename





gMonitorThreads = [".adclear:engine","n.adclear:proxy"]

fromaddr = "noreply@seven.com"
recipients = ['swang@seven.com']
toaddr = ", ".join(recipients)

mail_account = 'lashwang@outlook.com'
mail_passwd = 'meimei1985'
smtp_server = 'smtp-mail.outlook.com:587'


def main():
    check_device()

    while True:
        try:
            psAdclear = read_process_for_adclear()
            print str(datetime.datetime.now()) + ":find engine/proxy pids:" + str(psAdclear)
            for pid in psAdclear:
                read_task_info(int(pid))
            pass
        except Exception,e:
            print e





def check_device():
    errMsg = "No device connected,please check\n"
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
    errMsg = "No device connected,please check\n"
    output = commands.getstatusoutput('adb shell ps')
    psAdclear = []
    if output[0] != 0:
        sys.stderr.write(errMsg)
        exit(1)
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


def find_suspicious_task(pid,tid,taskName):
    trace_path = 'dalvik-dump.txt'
    cmd = "adb shell bugreport"
    #output = commands.getstatusoutput(cmd)
    cmd = 'adb shell su -c "cat /data/anr/traces.txt.bugreport"'
    output = commands.getstatusoutput(cmd)
    with open(trace_path, 'w') as file:
        file.write(output[1])
    msg = MIMEMultipart()
    msg['From'] = mail_account
    msg['To'] = toaddr
    msg['Subject'] = "find suspicious task {},pid/tid is {}/{}".format(taskName,pid,tid)
    msg.attach(MIMEText(msg['Subject'],_subtype='plain', _charset='utf-8'))
    with open(trace_path, "rb") as fil:
        part = MIMEApplication(
            fil.read(),
            Name=basename(trace_path)
        )
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(trace_path)
        msg.attach(part)


    server = smtplib.SMTP(smtp_server)
    server.ehlo()
    server.starttls()
    server.login(mail_account, mail_passwd)
    server.ehlo()
    server.sendmail(mail_account, recipients, msg.as_string())
    server.close()
    exit(0)
    pass

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
            print "find {} with pid/tid:{}/{}".format(taskName,pid,tid)
            if pid != tid:
                print "find suspicious task!!!!"
                find_suspicious_task(pid, tid, taskName)




if __name__ == "__main__":
    main()
