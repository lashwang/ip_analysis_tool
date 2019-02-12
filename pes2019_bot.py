#!/usr/bin/python
# -*- coding: utf-8 -*-



import fire
import pyautogui
from pywinauto.application import Application
import win32gui
import win32ui
import ctypes


MessageBox = ctypes.windll.user32.MessageBoxW
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible




PS_REMOTE_WINDOW_TITLE = "PS4遥控操作"
PS_MACRO_WINDOW_TITLE = "PS4 Macro"



all_window_titles = []



def enumHandler(hwnd, lParam):
    if win32gui.IsWindowVisible(hwnd):
        all_window_titles.append(win32gui.GetWindowText(hwnd))


def find_ps4_related_window():
    all_window_titles.clear()
    win32gui.EnumWindows(enumHandler, None)

    hld_ps4_macro = None
    hld_ps4_remote = None

    for titile in all_window_titles:
        if PS_MACRO_WINDOW_TITLE in titile:
            hld_ps4_macro = win32gui.FindWindow(None, titile)
            continue

        if PS_REMOTE_WINDOW_TITLE in titile:
            hld_ps4_remote = win32gui.FindWindow(None, titile)
            continue

    if not hld_ps4_macro:
        MessageBox(None, '请先打开PS Macro软件', '错误', 0)
        exit(-1)

    if not hld_ps4_remote:
        MessageBox(None, '请先打开PS Remote软件', '错误', 0)
        exit(-1)

    return (hld_ps4_remote,hld_ps4_macro)

def get_window_size(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    return (x,y,w,h)


class CmdInterface():
    def get_screen(self):
        im2 = pyautogui.screenshot('my_screenshot.png')
        pass

    def find_ps4_remote_screen(self):
        hld_ps4_remote = win32gui.FindWindow(None, PS_REMOTE_WINDOW_TITLE)
        if not hld_ps4_remote:
            MessageBox(None, '请先打开PS遥控软件', '错误', 0)
            exit(-1)

        hld_ps4_macro = win32gui.FindWindow(None, PS_MACRO_WINDOW_TITLE)
        if not hld_ps4_macro:
            MessageBox(None, '请先打开PS Macro软件', '错误', 0)
            exit(-1)

    def list_ps4_windows(self):
        hld_ps4_remote,hld_ps4_macro = find_ps4_related_window()
        print(hld_ps4_remote,hld_ps4_macro)
        win32gui.SetForegroundWindow(hld_ps4_remote)
        (x,y,w,h) = get_window_size(hld_ps4_remote)
        print(w,h)




def main():
    fire.Fire(CmdInterface)
    pass


if __name__ == "__main__":
    main()