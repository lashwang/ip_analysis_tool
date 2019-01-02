#!/usr/bin/python
# -*- coding: utf-8 -*-



import fire
from subprocess import call
import re
import os
import commands
import glob




port_query_reg_str = r"CSM\s+\[{}\].*client_src_port\s+(\d+),\s+csp_src_port\s+(\d+)"
adclear_apk_path = "adclear/build/outputs/apk/adclearInternal/debug"




def find_port_info_from_netlog(line,csm_id):
    if "addNetLogRecord:" not in line:
        return

    splited = line.split(",")
    csm_in_netlog = splited[-4]
    if int(csm_id, 16) == int(csm_in_netlog, 16):
        local_port = splited[-2]
        remote_port = splited[-1]
        if int(remote_port) == 0 or int(local_port) == 0:
            print "find zero port in netlogs:" + line
            return
        print "query result for [{}]:tcp.port eq {} or tcp.port eq {}".format(csm_id, local_port, remote_port)
        exit(0)


def find_host(line,saved_tables):
    if not "find host" in line:
        return
    reg_str = r"CSM\s+\[(\S+)\]\s+find host\s+(\S+)"
    matchObj = re.search(reg_str, line)
    if matchObj:
        csm_id = matchObj.group(1)
        host = matchObj.group(2)
        saved_tables[csm_id] = host


class QueryCmd():
    def get_port(self,logcat_path,csm_id):
        print "get_port,csm_id=" + str(csm_id)
        with open(str(logcat_path), "r") as ins:
            for line in ins:
                find_port_info_from_netlog(line,csm_id)
        pass

    def list_host(self,logcat_path="logcat.log"):
        '''
        CSM [0009801C] find host m.youtube.com
        '''
        hosts_table = {}

        with open(str(logcat_path), "r") as ins:
            for line in ins:
                find_host(line,hosts_table)

        for key,value in hosts_table.iteritems():
            print "{} -> {}".format(key,value)

    def get_tcpdump(self):
        cmd = "rm -rf trace/ "
        os.system(cmd)
        cmd = 'adb shell su -c "cp /data/data/com.seven.adclear/files/openchannel/ssl_dump.log /sdcard/trace/."'
        os.system(cmd)
        cmd = 'adb pull -a /sdcard/trace .'
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
        cmd = "adb shell mkdir /sdcard/trace/ "
        os.system(cmd)

    def stop_adclear(self):
        cmd = "adb shell ps"
        results = commands.getoutput(cmd).splitlines()
        for line in results[1:]:
            if "adclear" in line:
                pid = line.split()[1]
                cmd = 'adb shell su -c "kill -9 {}"'.format(pid)
                print "killing..{}".format(line)
                os.system(cmd)




    def query_crash(self,addr):
        cmd = "addr2line_android -p -C -i -f -e proxy/build/intermediates/ndkBuild/debug/obj/local/armeabi/libproxy.so {}".format(addr)
        results = commands.getoutput(cmd)
        print results

    def clear_logcat(self):
        cmd = "adb logcat -c"
        for num in range(0,5):
            os.system(cmd)

    def build_adclear(self):
        cmd = "rm -rf {}/*.apk".format(adclear_apk_path)
        os.system(cmd)
        cmd = "./gradlew assembleAdclearInternalDebug"
        os.system(cmd)

    def recreate_adclear(self):
        self.build_adclear()
        self.install_adclear()
        self.clear_logcat()


    def install_adclear(self):
        apk_list = glob.glob("{}/*.apk".format(adclear_apk_path))

        if apk_list is None or len(apk_list) == 0:
            print "no apk found"
            exit(0)

        cmd = "adb install -r {}".format(apk_list[0])
        os.system(cmd)


    def get_tombstone(self):
        cmd = 'adb shell su -c "cp -pFR /data/tombstones/ /sdcard/."'
        os.system(cmd)
        cmd = 'adb pull -a /sdcard/tombstones/ .'
        os.system(cmd)

def main():
    fire.Fire(QueryCmd)
    pass


if __name__ == "__main__":
    main()