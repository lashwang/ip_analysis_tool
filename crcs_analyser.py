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
import arrow



# define battery drop level
BATTERY_DROP_WATER_LEVEL = 4


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
    global df_all,df_power,df_netlog,crcs_start_time,df_power_fast
    file_object = open_file_input_string(f)
    df_all = pandas.read_csv(file_object,header=None,error_bad_lines=False)
    df_all[0] = pandas.to_datetime(df_all.iloc[:,0],format="%Y-%m-%d %H:%M:%S")
    crcs_start_time = df_all.iloc[0,0]
    df_power = df_all[df_all.iloc[:, 4] == 'battery']
    df_power = df_power.dropna(axis=1)
    df_power[5] = pandas.to_numeric(df_power[5])
    df_power[7] = pandas.to_numeric(df_power[7])/1000
    # get the fast power records.
    df_power_fast = df_power[df_power[7] <= BATTERY_DROP_WATER_LEVEL*60].copy()
    df_power_fast['end_time'] = df_power_fast[0]
    df_power_fast['start_time'] = df_power_fast['end_time'] - pandas.to_timedelta(df_power_fast[7],'s')
    df_netlog = df_all[df_all[2] == 'netlog'].copy()
    generate_battery_report()
    pass

def generate_battery_report():
    global df_netlog_select
    df_netlog_select = pandas.DataFrame()
    for index, row in df_power_fast.iterrows():
        start_time = row['start_time']
        end_time = row['end_time']
        df_netlog_temp = df_netlog[(df_netlog[0] >= start_time) & (df_netlog[0] <= end_time)]
        df_netlog_select = df_netlog_select.append(df_netlog_temp)
        pass
    df_app_list = df_netlog_select.groupby(11)[0].nunique()
    df_app_error_number = df_netlog_select[df_netlog_select[22] != 0].groupby([11, 22]).size()

    pass


def default():
    parse_crcs_from_file('data/Crcs_#7515.gz')

class CRCSAnaLyser(object):
    def file(self,f):
        parse_crcs_from_file(f)

    def folder(self,d):
        pass



def main():
    global wb
    wb = Workbook()
    if len(sys.argv) == 1:
        fire.Fire(default)
    else:
        fire.Fire(CRCSAnaLyser)
    wb.save(arrow.now().format("YYYY_MM_DD") + ".xlsx")


if __name__ == "__main__":
    main()