#!/usr/bin/python
# -*- coding: utf-8 -*-



import fire
import pyautogui
from pywinauto.application import Application


class CmdInterface():
    def get_screen(self):
        windows = Application().
        im2 = pyautogui.screenshot('my_screenshot.png')
        pass

def main():
    fire.Fire(CmdInterface)
    pass


if __name__ == "__main__":
    main()