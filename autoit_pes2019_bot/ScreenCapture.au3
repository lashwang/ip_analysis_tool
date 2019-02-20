#AutoIt3Wrapper_UseX64=n ; In order for the x86 DLLs to work
#include-once
#include <ScreenCapture.au3>

Global $win_title = "PS4Ò£¿Ø²Ù×÷"

DirCreate(@MyDocumentsDir & "\test_folder\")
AdlibRegister("screen_capture",1*1000)


WinActive($win_title)
Sleep(1*1000)
Global $hWnd = WinWaitActive($win_title,"",120)


Func screen_capture()
	Local $hBitmap = _ScreenCapture_CaptureWnd("", $hWnd)
	_ScreenCapture_SaveImage(@MyDocumentsDir&"\test_folder\image_"&@HOUR&"_"&@MIN&"_"&@SEC&".bmp", $hBitmap)
	_WinAPI_DeleteObject($hBitmap)
 EndFunc

