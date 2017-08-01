#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import commands
import arrow
import time
import re



logger = logging.getLogger(__name__)


WAKELOCK_DETECT_TIME = 5



def parse_wakelock_output(output):
    all_lines = output.split("\n")
    wakelock_logs = []
    for index,line in enumerate(all_lines):
        if "Wake Locks:" in line:
            result = re.match("Wake Locks: size=(\d+)",line)
            if result:
                size = int(result.group(1))
                wakelock_logs = all_lines[index+1:index+size+1]

    return wakelock_logs


def run_dumpsys():
    output = commands.getstatusoutput("adb shell dumpsys power")[1]
    wakelock_logs = parse_wakelock_output(output)
    now = arrow.utcnow().format("[YYYY-MM-DD HH:mm:ss]")
    f = open("wakelock.log","a+")
    logs = ""
    for line in wakelock_logs:
        logs += now + line.strip() + "\n"
    f.write(logs)
    f.close()


def main():
    while True:
        run_dumpsys()
        time.sleep(WAKELOCK_DETECT_TIME)
    pass

if __name__ == "__main__":
    main()


