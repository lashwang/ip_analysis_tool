#!/usr/bin/python
# -*- coding: utf-8 -*-



import fire
from subprocess import call
import re
import os
import commands





port_query_reg_str = r"CSM\s+\[{}\].*client_src_port\s+(\d+),\s+csp_src_port\s+(\d+)"


class QueryCmd():
    def get_port(self,logcat_path,csm_id):
        print "get_port,csm_id=" + csm_id
        with open(logcat_path, "r") as ins:
            for line in ins:
                if csm_id not in line:
                    continue
                if "client_src_port" not in line and "csp_src_port" not in line:
                    continue
                #print line
                reg_str = port_query_reg_str.format(csm_id)
                matchObj = re.search(reg_str, line)
                if matchObj:
                    local_port = matchObj.group(1)
                    remote_port = matchObj.group(2)
                    print "query result for [{}]:tcp.port eq {} or tcp.port eq {}".format(csm_id,local_port,remote_port)
                    return

        pass

    def get_tcpdump(self):
        cmd = 'adb shell su -c "cp /data/data/com.seven.adclear/files/openchannel/ssl_dump.log /sdcard/trace/."'
        os.system(cmd)
        cmd = 'adb pull /sdcard/trace .'
        os.system(cmd)

        pass

    def stop_tcpdump(self):
        cmd = "adb shell ps"
        results = commands.getoutput(cmd).splitlines()
        for line in results[1:]:
            if "mightydumpty" in line:
                pid = line.split()[1]
                cmd = 'adb shell su -c "kill -9 {}"'.format(pid)
                print "killing..{}".format(line)
                os.system(cmd)

        cmd = "adb shell rm -rf /sdcard/trace/ "
        os.system(cmd)

    def query_crash(self,addr):
        cmd = "addr2line_android -p -C -i -f -e proxy/build/intermediates/ndkBuild/debug/obj/local/armeabi/libproxy.so {}".format(addr)
        results = commands.getoutput(cmd)
        print results


def main():
    fire.Fire(QueryCmd)
    pass


if __name__ == "__main__":
    main()