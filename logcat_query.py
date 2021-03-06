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


default_flavor = "AdclearInternalDev"
asan_flavor = "AdclearAsanDev"


port_query_reg_str = r"CSM\s+\[{}\].*client_src_port\s+(\d+),\s+csp_src_port\s+(\d+)"
adclear_apk_path = "app/build/outputs/apk/{}/debug".format(default_flavor)


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
    '''
    CSM [000E8009] clienthello_parse host www.google.com, c_hello_md5 36781B4C62E4D394F6F4EA1CB5FD7F97 length 508, tlsextslen 401
    '''

    reg_str = r"CSM\s+\[(\S+)\]\s+clienthello_parse host (\S+),"
    matchObj = re.search(reg_str, line)
    if matchObj:
        csm_id = matchObj.group(1)
        host = matchObj.group(2)
        saved_tables[csm_id] = host


def find_csm(line):
    '''
    [Native]proxy: 06-12 11:47:40.854 +0800 4468 [FT] [Session.cpp:91] (0) - [tcp0] CSM [00068004] Creating Session for fd 6
    '''
    if not "Creating Session for fd" in line:
        return None
    reg_str = r"\[(\S+)\]\s+CSM\s+\[(\S+)\]\s+Creating Session for fd"
    matchObj = re.search(reg_str, line)
    reg_str2 = r"\[Native\]proxy: (\S+) (\S+)"
    matchObj2 = re.search(reg_str2, line)
    if matchObj:
        thread_id = matchObj.group(1)
        csm_id = matchObj.group(2)
        date = matchObj2.group(1)
        time = matchObj2.group(2)
        return (thread_id,csm_id,date + " " + time)

    return None


def find_in_out_fd(line,in_fd_table,out_fd_table,in_port_table,out_port_table):
    '''
    CSM [00068001] create OUT endpoint for fd:97,port:40161
    '''

    reg_str = r"\CSM\s+\[(\S+)\]\s+create (\w+) endpoint for fd:(\d+),port:(\d+)"
    matchObj = re.search(reg_str, line)
    if matchObj:
        csm_id = matchObj.group(1)
        str = matchObj.group(2)
        fd = matchObj.group(3)
        port = matchObj.group(4)
        if "IN" == str:
            in_fd_table[csm_id] = fd
            in_port_table[csm_id] = port
        else:
            out_fd_table[csm_id] = fd
            out_port_table[csm_id] = port


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
        [tcp0] CSM [00068001] Creating Session for fd 6
        '''
        csm_table = {}
        thread_table = {}
        in_fd_table = {}
        out_fd_table = {}
        in_port_table = {}
        out_port_table = {}
        host_table = {}
        with open(str(logcat_path), "r") as ins:
            for line in ins:
                ret = find_csm(line)
                if ret:
                    csm = ret[1]
                    thread_name = ret[0]
                    csm_table[ret[2]] = ret[1]
                    thread_table[csm] = thread_name
                find_in_out_fd(line,in_fd_table,out_fd_table,in_port_table,out_port_table)
                find_host(line,host_table)


        for time,csm_id in sorted(csm_table.items()):
            print "time:{},thread:{},csm_id:{},in out fd:[{:>5}:{:>5}],in out port:[{:>5}:{:>5}],host:{}"\
                .format(time,
                        thread_table[csm_id],
                        csm_id,
                        in_fd_table.get(csm_id),
                        out_fd_table.get(csm_id),
                        in_port_table.get(csm_id),
                        out_port_table.get(csm_id),
                        host_table.get(csm_id),
                        )

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
        ndk_path = os.environ['ANDROID_NDK_HOME']
        addr2line_path = ndk_path + "/toolchains/llvm/prebuilt/darwin-x86_64/bin/arm-linux-androideabi-addr2line"
        lib_path = "proxy/build/intermediates/ndkBuild/debug/obj/local/armeabi-v7a/libproxy.so"
        cmd = "{} -p -C -i -f -e {} {}".format(addr2line_path,lib_path,sys.argv[2])
        print cmd
        results = commands.getoutput(cmd)
        print results

    def query_crash64(self,addr):
        ndk_path = os.environ['ANDROID_NDK_HOME']
        addr2line_path = ndk_path + "/toolchains/llvm/prebuilt/darwin-x86_64/bin/aarch64-linux-android-addr2line"
        lib_path = "proxy/build/intermediates/ndkBuild/debug/obj/local/arm64-v8a/libproxy.so"
        cmd = "{}  -p -C -i -f -e {} {}".format(addr2line_path,lib_path,sys.argv[2])
        print cmd
        results = commands.getoutput(cmd)
        print results


    def clear_logcat(self):
        cmd = "adb logcat -c"
        for num in range(0,5):
            os.system(cmd)

    def build_adclear(self,flavor=default_flavor,*args):
        build_args = get_build_args(args)
        cmd = "rm -rf {}/*.apk".format(adclear_apk_path)
        os.system(cmd)
        cmd = "./{} assemble{}Debug -PnativeFlavor=nativeNoCrashCollect {}".format(build_cmd,flavor,build_args)
        print cmd
        os.system(cmd)

    def build_adclear_multipleabi(self):
        self.build_adclear(default_flavor," -PnativeFlavor=nativeNoCrashCollect -PmultipleAbi=true")
        pass


    def build_adclear_asan(self):
        self.build_adclear(asan_flavor,"-PuseAsan=true -PnativeFlavor=nativeAsan")

    def build_adclear_clean(self):
        cmd = "./{} clean".format(build_cmd)
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

    def obj_dump64(self,path):
        ndk_path = os.environ['ANDROID_NDK_HOME']
        objdump_path = ndk_path + "/toolchains/llvm/prebuilt/darwin-x86_64/bin/aarch64-linux-android-objdump"
        base = os.path.basename(path)
        name = os.path.splitext(base)[0]
        cmd = "find proxy/build/intermediates/ndkBuild/debug/obj/local/arm64-v8a/objs-debug/proxy/ -name {}.o".format(
            name)
        print cmd
        results = commands.getoutput(cmd).splitlines()
        print results
        index = 1
        for file in results:
            cmd = "{} -d -l -S -C {}".format(objdump_path,file)
            output_name = "{}.o.{}.txt".format(name, index)
            results = commands.getoutput(cmd)
            index = index + 1
            with open(output_name, 'a') as the_file:
                the_file.write(results)

    def obj_dump_so(self):
        cmd = "android-objdump -t proxy/build/intermediates/ndkBuild/debug/obj/local/armeabi/libproxy.so"
        output_name = "libproxy.so.map"
        results = commands.getoutput(cmd)
        with open(output_name, 'a') as the_file:
            the_file.write(results)

    def reset_bc_tool(self):
        cmd = "sudo rm -rf /Users/simon/Library/Application Support/Beyond Compare/registry.dat"
        os.system(cmd)

    def parse_ssl_compare_log(self,path = "logcat.log"):
        bc_keypair_time_list = []
        openssl_keypair_time_list = []
        bc_cert_gen_time_list = []
        openssl_cert_gen_time_list = []
        with open(str(path), "r") as ins:
            for line in ins:
                reg_str = r"KeyPair time in BC:(\d+)"
                matchObj = re.search(reg_str, line)
                if matchObj:
                    bc_keypair_time = int(matchObj.group(1))
                    bc_keypair_time_list.append(bc_keypair_time)
                    continue

                reg_str = r"Diff from last:(\d+)"
                matchObj = re.search(reg_str, line)
                if matchObj:
                    time = int(matchObj.group(1))

                    if "https_task.cpp:507" in line:
                        openssl_keypair_time_list.append(time)
                        continue

                    if "https_task.cpp:509" in line:
                        openssl_cert_gen_time_list.append(time)
                        continue

                    if "https_task.cpp:528" in line:
                        bc_cert_gen_time_list.append(time)
                        continue

        print "bc keypair time:",bc_keypair_time_list
        print "openssl keypair time:",openssl_keypair_time_list
        print "bc cert-gen time:",bc_cert_gen_time_list
        print "openssl cert-gen time:",openssl_cert_gen_time_list


    def load_der_cert(self,path = "adclear.crt"):
        cmd = "openssl x509 -inform der -in {} -text".format(path)
        os.system(cmd)

    def get_standby_bucket(self,package="gcm.play.android.samples.com.gcmquickstart"):
        cmd = "adb shell am get-standby-bucket {}".format(package)
        os.system(cmd)

    def set_standby_bucket(self,package="gcm.play.android.samples.com.gcmquickstart"):
        cmd = "adb shell am set-standby-bucket {} rare".format(package)
        os.system(cmd)
        self.get_standby_bucket(package)

    def restart_boolloader(self):
        cmd = "adb reboot bootloader"
        os.system(cmd)

    def list_apps(self):
        cmd = "adb shell pm list packages -f -U"
        os.system(cmd)

    def list_net_ports(self):
        cmd = "adb shell netstat -lntu"
        os.system(cmd)

def main():
    fire.Fire(QueryCmd)
    pass


if __name__ == "__main__":
    main()