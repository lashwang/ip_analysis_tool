#!/usr/bin/python
# -*- coding: utf-8 -*-



import fire
import pyautogui
import pywinauto
from pywinauto.application import Application
#install win32gui manually from https://github.com/mhammond/pywin32/releases
import win32gui
import win32ui
import ctypes
import win32con
import time
import os
import cv2
import numpy as np
import traceback

MessageBox = ctypes.windll.user32.MessageBoxW
# EnumWindows = ctypes.windll.user32.EnumWindows
# EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
# GetWindowText = ctypes.windll.user32.GetWindowTextW
# GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
# IsWindowVisible = ctypes.windll.user32.IsWindowVisible




PS_REMOTE_WINDOW_TITLE = "PS4遥控操作"
PS_MACRO_WINDOW_TITLE = "PS4 Macro"
PS_IMG_SEARCH_PATH = "./pes2019_img_search/"
PS_REMOTE_INSTALLED_PATH = 'C:\Program Files (x86)\Sony\PS4 Remote Play\RemotePlay.exe'

all_window_titles = []
image_search_dict = {}


IMAGE_PS_ICON_ID = 1
IMAGE_PS_ICON_NAME = "ps_remote_logo.png"


image_search_dict[IMAGE_PS_ICON_ID] = IMAGE_PS_ICON_NAME







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


def get_img_recoure_path(img_id):
    return os.path.join(PS_IMG_SEARCH_PATH,image_search_dict[img_id])

def press_ps4_as_forground():
    image = get_img_recoure_path(IMAGE_PS_ICON_ID)
    try:
        pos = pyautogui.locateCenterOnScreen(image)
        print(pos)
        pyautogui.moveTo(pos.x,pos.y)
        pyautogui.click()
    except Exception as ex:
        print(ex)
        im = pyautogui.screenshot('my_screenshot.png')
        img_rgb = np.array(im)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(image, 0)
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        print("find ps screen:",min_val, max_val, min_loc, max_loc)


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
            try:
                ps4_hwnd = win32gui.GetForegroundWindow()
                text = win32gui.GetWindowText(ps4_hwnd)
                rect = win32gui.GetWindowRect(ps4_hwnd)
                print("get focus window:" + text)
                print("focus window area:" + str(rect))
                if PS_REMOTE_WINDOW_TITLE not in text:
                    press_ps4_as_forground()
                    time.sleep(5)
                    continue
                screen_now = pyautogui.screenshot()
                time.sleep(3)
            except Exception as ex:
                print(ex)
                traceback.print_exc()
                pyautogui.screenshot("process_error.png")
                break

    def open_game_window(self):
        app = Application(backend="uia").start(PS_REMOTE_INSTALLED_PATH)
        # print(app)
        #app = Application().Start(cmd_line=u'"C:\\Program Files (x86)\\Sony\\PS4 Remote Play\\RemotePlay.exe" ')
        windowsformswindowappbarad = app[u'PS4\u9065\u63a7\u64cd\u4f5c']

        print(windowsformswindowappbarad)
        # windowsformswindowappbarad.Wait('ready')
        # windowsformsbuttonappbarad = windowsformswindowappbarad[u'\u5f00\u59cb']
        # windowsformsbuttonappbarad.Click()
        pass



def main():
    fire.Fire(CmdInterface)
    pass


if __name__ == "__main__":
    main()