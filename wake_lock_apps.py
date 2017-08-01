#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import re


logger = logging.getLogger(__name__)


'''
﻿Package [com.samsung.android.app.ledcoverdream] (92d7672):
'''
def dump_wakelock_apps(content):
    curr_app = None
    is_shared_user = False
    app_list = []
    shared_app_list = []
    for line in content:
        if "Package [" in line:
            result = re.match("(\s+)(Package|SharedUser)(\s+)\[(\S+)\](.*)",line)
            if result:
                app = result.group(4)
                curr_app = app
                is_shared_user = False

        if "SharedUser [" in line:
            result = re.match("(\s+)(Package|SharedUser)(\s+)\[(\S+)\](.*)",line)
            if result:
                app = result.group(4)
                curr_app = app
                is_shared_user = True


        if "android.permission.WAKE_LOCK:" in line:
            if not is_shared_user:
                app_list.append(curr_app)
            else:
                shared_app_list.append(curr_app)

    print "\n".join(app_list)

def main():
    fname = "data/package.txt"
    with open(fname) as f:
        content = f.readlines()

    dump_wakelock_apps(content)





if __name__ == "__main__":
    main()