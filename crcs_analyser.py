#!/usr/bin/python
# -*- coding: utf-8 -*-

import fire
from zipfile import ZipFile, is_zipfile
import StringIO
import fileinput
import sys
import gzip
import binascii
import pandas
from openpyxl import Workbook,load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from collections import OrderedDict
import arrow
import os, fnmatch
import gc

# define battery drop level
BATTERY_DROP_WATER_LEVEL = 4
title_exist = False

def is_gz_file(filepath):
    with open(filepath, 'rb') as test_f:
        return binascii.hexlify(test_f.read(2)) == b'1f8b'

def open_file_input_string(input_file):
    if is_gz_file(input_file):
        with gzip.open(input_file, 'rb') as f:
            file_content = f.read()
        file_object = StringIO.StringIO(file_content)
    else:
        file_object = fileinput.input(input_file)

    return file_object


def parse_crcs_from_file(f):
    global df_all,df_power,df_netlog,df_system,df_backlight,df_deviceinfo,df_memory
    global crcs_start_time,crcs_end_time,df_power_fast,user_id,orig_file,total_crcs_number
    df_all = pandas.DataFrame()
    df_power_fast = pandas.DataFrame()
    df_system = pandas.DataFrame()
    df_netlog = pandas.DataFrame()
    df_power = pandas.DataFrame()
    df_memory = pandas.DataFrame()

    file_object = open_file_input_string(f)
    #print "read_csv"
    df_all = pandas.read_csv(file_object,header=None,names = list(range(0,100)))
    print "read_csv success,record number:" + str(df_all.shape[0])
    total_crcs_number = df_all.shape[0]
    #df_all = df_all.dropna(axis=1)
    df_all[0] = pandas.to_datetime(df_all.iloc[:,0],format="%Y-%m-%d %H:%M:%S",errors='coerce')
    #print "convert to datatime"
    crcs_start_time = df_all.iloc[0,0]
    crcs_end_time = df_all.iloc[-1,0]
    orig_file = f
    user_id = df_all.iloc[0,1]
    df_power = df_all[df_all.iloc[:, 4] == 'battery']
    if df_power.shape[0] == 0:
        return
    df_power = df_power.dropna(axis=1)
    df_power[5] = pandas.to_numeric(df_power[5])
    df_power[7] = pandas.to_numeric(df_power[7])/1000
    # get the fast power records.
    df_power_fast = df_power[df_power[7] <= BATTERY_DROP_WATER_LEVEL*60].copy()
    df_power_fast['end_time'] = df_power_fast[0]
    df_power_fast['start_time'] = df_power_fast['end_time'] - pandas.to_timedelta(df_power_fast[7],'s')
    df_netlog = df_all[df_all[2] == 'netlog'].copy()

    # process system log
    df_system = df_all[df_all[2] == 'system']
    df_backlight = df_system[df_system[4] == 'backlight'].copy()
    df_backlight = df_backlight.dropna(axis=1)
    df_deviceinfo = df_system[df_system[4] == 'dev_info'].copy()
    df_deviceinfo = df_deviceinfo.dropna(axis=1)

    df_memory = df_system[df_system[4] == 'memory'].copy()


    generate_basic_battery_report()



    pass

def calc_screen_battery_usage():
    global avg_battery_drop_speed_screen_on,avg_battery_drop_speed_screen_off
    avg_battery_drop_speed_screen_on = 0
    avg_battery_drop_speed_screen_off = 0
    df_power_backlight = df_all[df_all[4].isin(['battery','backlight'])].copy()
    df_power_backlight = df_power_backlight.reset_index()
    df_power_screen_on = pandas.DataFrame()
    df_power_screen_off = pandas.DataFrame()
    df_power_temp = pandas.DataFrame()
    pre_screen_state = -1
    now_screen_events = -1
    for index,row in df_power_backlight.iterrows():
        if row[2] == 'power':
            df_power_temp = df_power_temp.append(row)
        elif row[2] == 'system':
            if int(row[5]) == 100:
                now_screen_events = 1
            elif int(row[5]) == 0:
                now_screen_events = 0

            if now_screen_events == pre_screen_state:
                continue

            if now_screen_events:
                df_power_screen_off = df_power_screen_off.append(df_power_temp)
            else:
                df_power_screen_on = df_power_screen_on.append(df_power_temp)

            pre_screen_state = now_screen_events
            df_power_temp.drop(df_power_temp.index, inplace=True)



            pass
        # end if
        pass
    # end for
    if df_power_screen_on.shape[0] != 0:
        df_power_screen_on[7] = pandas.to_numeric(df_power_screen_on[7]) / 1000
        avg_battery_drop_speed_screen_on = df_power_screen_on[7].mean()\

    if df_power_screen_off.shape[0] != 0:
        df_power_screen_off[7] = pandas.to_numeric(df_power_screen_off[7]) / 1000
        avg_battery_drop_speed_screen_off = df_power_screen_off[7].mean()

    pass


def generate_basic_battery_report():
    global title_exist
    avg_battery_drop_speed = df_power[7].mean()
    device_mode = "unknown"
    device_version = "unknown"
    df_device = df_deviceinfo[df_deviceinfo[5] == '0']
    if df_device.shape[0] > 0:
        device_mode = df_device.iloc[0,:][6]
        device_version = df_device.iloc[0,:][7]
        pass

    calc_screen_battery_usage()
    result = OrderedDict()
    result['user'] = user_id
    result['total_crcs_number'] = total_crcs_number
    result['ave_battery_speed'] \
        = '{}%/{}'.format(round(3600/avg_battery_drop_speed,2),int(avg_battery_drop_speed))

    if avg_battery_drop_speed_screen_on != 0:
        result['screen_on_power_speed'] \
            = '{}%{}'.format(round(3600/avg_battery_drop_speed_screen_on,2),int(avg_battery_drop_speed_screen_on))
    else:
        result['screen_on_power_speed'] = "NA"

    if avg_battery_drop_speed_screen_off:
        result['screen_off_power_speed'] \
            = '{}%{}'.format(round(3600/avg_battery_drop_speed_screen_off,2),int(avg_battery_drop_speed_screen_off))
    else:
        result['screen_off_power_speed'] = "NA"
    result['device_mode'] = device_mode
    result['device_version'] = device_version
    result['start_time_utc'] = crcs_start_time
    result['end_time_utc'] = crcs_end_time
    result['source_file'] = orig_file
    if not title_exist:
        ws_basic.append(result.keys())
        title_exist = True
    ws_basic.append(result.values())

    pass


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename



def parser_crcs_from_dir(f):
    for filename in find_files(f, '*.*'):
        print 'Found file:', filename
        parse_crcs_from_file(filename)


        #gc.collect()
    pass

class CRCSAnaLyser(object):
    def parse(self,f):
        if os.path.isdir(f):
            parser_crcs_from_dir(f)
        else:
            parse_crcs_from_file(f)
        pass

    def test_parse_crcs_file(self):
        parse_crcs_from_file('data/Crcs_#7515.gz')

    def test_parse_crcs_folder(self):
        parser_crcs_from_dir('data/crcs_test_folder')
        pass



def main():
    global wb,ws_basic
    wb = Workbook()
    ws_basic = wb.active
    ws_basic.title = "basic battery info"
    fire.Fire(CRCSAnaLyser)
    wb.save("battery_report_" + arrow.now().format("YYYY_MM_DD") + ".xlsx")


def on_file_uploaded(file,output_path):
    global wb, ws_basic
    wb = Workbook()
    ws_basic = wb.active
    ws_basic.title = "basic battery info"
    parse_crcs_from_file(file)
    filename = user_id + ".xlsx"
    wb.save(output_path + "/" + filename)
    return filename

if __name__ == "__main__":
    main()