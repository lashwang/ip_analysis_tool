#include-once
#include <Timers.au3>
#include <ScreenCapture.au3>
#include <GUIConstantsEx.au3>
#include "log4a.au3"


$remoteplay = "C:\Program Files (x86)\Sony\PS4 Remote Play\RemotePlay.exe"
$rplay_class = "WindowsForms10.BUTTON.app.0.141b42a_r9_ad1"
$btn_start = "开始"
$win_title = "PS4遥控操作"


_log4a_SetEnable()
DirCreate(@MyDocumentsDir & "\test_folder\")
Run($remoteplay)
Global $hWnd = WinWaitActive($win_title,$btn_start,120)
If $hWnd == 0 Then
   _log4a_Info("Open PS4 remote timeout")
   Exit
EndIf

_log4a_Info("PS4 remote started.")
Sleep(1*1000)
; press start
ControlClick($hWnd, "",$btn_start)
Sleep(1*1000)


Global $hCtrl = 0, $Waiting = True
While ($Waiting)
   If $Waiting And WinExists($win_title) Then
	  $hCtrl = ControlGetHandle($win_title, "", "[NAME:ViewPanel]")
		 If $hCtrl Then
			; we got the handle, so the button is there
			; now do whatever you need to do
			_log4a_Info("Find Viewpanel!!!");
			$Waiting = False
	  EndIf
   EndIf
   Sleep(2*1000)
WEnd
WinActive($win_title)
Sleep(1*1000)
$hWnd = WinWaitActive($win_title,"",120)
_log4a_Info("Start to play games")
$hBitmap = _ScreenCapture_CaptureWnd("", $hWnd)
_ScreenCapture_SaveImage(@MyDocumentsDir&"\test_folder\"&@HOUR&@MIN&@SEC&"Image.jpg", $hBitmap)


#comments-start
While 1
$hBitmap = _ScreenCapture_CaptureWnd("", $hWnd)
_ScreenCapture_SaveImage(@MyDocumentsDir&"\test_folder\"&@HOUR&@MIN&@SEC&"Image.jpg", $hBitmap)
Sleep(1*1000)
WEnd
#comments-end

#comments-start
; press esc for 3 times
_log4a_Info("Begin to send esc")
For $i = 1 To 20
   Send("{ESC}")
   Sleep(1*1000)
Next
_log4a_Info("End to send esc")

; press enter for 3 times
_log4a_Info("Begin to send enter")
For $i = 1 To 20
   Send("{Enter}")
   Sleep(1*1000)
Next
_log4a_Info("End to send enter")



_log4a_Info("Begin to send esc")
For $i = 1 To 40
   Send("{ESC}")
   Sleep(1*1000)
Next
_log4a_Info("End to send esc")


While 1
   Send("{Enter}")
   Sleep(1000)
WEnd
#comments-end




