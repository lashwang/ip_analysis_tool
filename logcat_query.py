#!/usr/bin/python
# -*- coding: utf-8 -*-



import fire
from subprocess import call
import re
import os
import commands
import glob
import platform
import sys


default_flavor = "adclearInternalDev"

port_query_reg_str = r"CSM\s+\[{}\].*client_src_port\s+(\d+),\s+csp_src_port\s+(\d+)"
adclear_apk_path = "adclear/build/outputs/apk/{}/debug".format(default_flavor)


build_cmd = "gradlew"

if "cygwin" in platform.system():
    build_cmd = "gradlew.bat"


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


def find_elem_hide_url(line,saved_tables):
    '''
    01-02 15:36:18.883 11958 12306 V [Native]proxy: 01-02 15:36:18.883 +0800 12306 [T]
    [http_task.cpp:646] (0) -
    CSM [000C806E] HTRX [000C030E] Enable element hide for url
    https://m.youtube.com/csi_204?GetBrowse_rid=0x38f07bc418e6f1f7&action=home&csn=8mksXPiPOIrhigT5u5XQBg&c=MWEB&cver=2.20181220&h2pc=0&is_nav=1&pis=d&p=HTTP/1.1&rc=mcj&rt=ai.2962,apr.3001,srt.1805,fpt.3068,nreqs.1209,nress.1805,nrese.2680,ntcps.22,ntcpe.1208,nstcps.348,rsf_mcj.1873,rse_mcj.1873,pdr.3035,ips.3060,ipc.3106,cpt.3107,vpl.3226,aft.3107,ps.3310&s=youtube_mobile&st=717&t=tcp&v=2&vpil=2&vpni=2&yt_fn=what_to_watch&yt_li=1&yt_lt=cold&yt_sts=n&yt_vis=1
    :return:
    '''
    if not "Enable element hide for url" in line:
        return

    reg_str = r"CSM\s+\[(\S+)\].+Enable element hide for url (.*)"

    matchObj = re.search(reg_str, line)
    if matchObj:
        csm_id = matchObj.group(1)
        url = matchObj.group(2)
        saved_tables[csm_id] = url


def find_body_hack_type(line,saved_tables):
    '''
    CSM [000B806D] on_body_part body_hack_type 4 len 10744, elem_hide_state 1, isChunk 1, isGzip false
    '''
    if not "body_hack_type" in line:
        return

    reg_str = r"CSM\s+\[(\S+)\].+body_hack_type (\w+)"
    matchObj = re.search(reg_str, line)
    if matchObj:
        csm_id = matchObj.group(1)
        hack_type = matchObj.group(2)
        if "0x" in hack_type:
            hack_type = int(hack_type,16)

        saved_tables[csm_id] = int(hack_type)

def get_build_args(args):
    params = ""
    for arg in args:
        params += " " + str(arg)

    return params

class QueryCmd():
    def get_port(self,csm_id,logcat_path="logcat.log"):
        print "get_port,csm_id=" + str(csm_id)
        with open(str(logcat_path), "r") as ins:
            for line in ins:
                find_port_info_from_netlog(line,csm_id)
        pass

    def list_traffic(self,logcat_path="logcat.log"):
        '''
        CSM [0009801C] find host m.youtube.com
        '''
        hosts_table = {}
        elmhide_url_table = {}
        hack_type_table = {}
        with open(str(logcat_path), "r") as ins:
            for line in ins:
                find_host(line,hosts_table)
                find_elem_hide_url(line,elmhide_url_table)
                find_body_hack_type(line,hack_type_table)
        for key,value in hosts_table.iteritems():
            hack_type = hack_type_table.get(key,0)
            url = elmhide_url_table.get(key,"")
            if hack_type > 0:
                print "{} -> host:{},hack_type:{},url:{}".format(key,value,hack_type,url)


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
        cmd = "addr2line_android -p -C -i -f -e proxy/build/intermediates/ndkBuild/debug/obj/local/armeabi/libproxy.so {}".format(sys.argv[2])
        print cmd
        results = commands.getoutput(cmd)
        print results

    def clear_logcat(self):
        cmd = "adb logcat -c"
        for num in range(0,5):
            os.system(cmd)

    def build_adclear(self,*args):
        build_args = get_build_args(args)
        cmd = "rm -rf {}/*.apk".format(adclear_apk_path)
        os.system(cmd)
        cmd = "./{} assemble{} {}".format(build_cmd,default_flavor,build_args)
        print cmd
        os.system(cmd)

    def recreate_adclear(self,*args):
        self.build_adclear(*args)
        self.install_adclear()
        self.clear_logcat()


    def install_adclear(self):
        apk_list = glob.glob("{}/*.apk".format(adclear_apk_path))

        if apk_list is None or len(apk_list) == 0:
            print "no apk found"
            exit(0)

        cmd = "adb install -r {}".format(apk_list[0])
        print cmd
        os.system(cmd)


    def get_tombstone(self):
        cmd = 'adb shell su -c "cp -pFR /data/tombstones/ /sdcard/."'
        os.system(cmd)
        cmd = 'adb pull -a /sdcard/tombstones/ .'
        os.system(cmd)

    def obj_dump(self,path):
        base = os.path.basename(path)
        name = os.path.splitext(base)[0]
        cmd = "find proxy/build/intermediates/ndkBuild/debug/obj/local/armeabi/objs-debug/proxy/ -name {}.o".format(name)
        print cmd
        results = commands.getoutput(cmd).splitlines()
        print results
        index = 1
        for file in results:
            cmd = "android-objdump -d -l -S -C {}".format(file)
            output_name = "{}.o.{}.txt".format(name,index)
            results = commands.getoutput(cmd)
            index = index + 1
            with open(output_name, 'a') as the_file:
                the_file.write(results)


def main():
    fire.Fire(QueryCmd)
    pass


if __name__ == "__main__":
    main()