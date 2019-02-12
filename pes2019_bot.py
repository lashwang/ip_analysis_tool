#!/usr/bin/python
# -*- coding: utf-8 -*-



import fire
import pyautogui
from pywinauto.application import Application
import win32gui
import win32ui
import ctypes
import win32con
import time
import os

MessageBox = ctypes.windll.user32.MessageBoxW
# EnumWindows = ctypes.windll.user32.EnumWindows
# EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
# GetWindowText = ctypes.windll.user32.GetWindowTextW
# GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
# IsWindowVisible = ctypes.windll.user32.IsWindowVisible




PS_REMOTE_WINDOW_TITLE = "PS4遥控操作"
PS_MACRO_WINDOW_TITLE = "PS4 Macro"
PS_IMG_SEARCH_PATH = "./pes2019_img_search"


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


def get_window_screenshot(hwnd):
    (x,y,w,h) = get_window_size(hwnd)
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0, 0), (w, h), dcObj, (0, 0), win32con.SRCCOPY)
    dataBitMap.SaveBitmapFile(cDC, "test.bmp")
    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())


def press_ps4_as_forground():
    pos = pyautogui.locateCenterOnScreen(os.path.join(PS_IMG_SEARCH_PATH,'ps_remote_logo.png'),confidence=0.9)
    print(pos)

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
        win32gui.MoveWindow(hld_ps4_remote, 0, 0, 1920, 1080, True)

        (x,y,w,h) = get_window_size(hld_ps4_remote)
        print(w,h)
        get_window_screenshot(hld_ps4_remote)


    def waiting_ps4_as_foreground(self):
        while True:
            text = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            print("get focus window:" + text)
            if PS_REMOTE_WINDOW_TITLE in text:
                break
            time.sleep(3)

        pyautogui.screenshot('my_screenshot.png')

    def pes2019_bot_loop(self):
        while True:
            text = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            print("get focus window:" + text)
            if PS_REMOTE_WINDOW_TITLE not in text:
                press_ps4_as_forground()
                time.sleep(3)
                continue
            screen_now = pyautogui.screenshot()

            time.sleep(3)

def main():
    fire.Fire(CmdInterface)
    pass


if __name__ == "__main__":
    main()