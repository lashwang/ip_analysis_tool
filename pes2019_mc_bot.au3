#include-once
#include <Timers.au3>
#include "log4a.au3"
#include <ScreenCapture.au3>

$remoteplay = "C:\Program Files (x86)\Sony\PS4 Remote Play\RemotePlay.exe"
$rplay_class = "WindowsForms10.BUTTON.app.0.141b42a_r9_ad1"
$btn_start = "开始"
$win_title = "PS4遥控操作"


_log4a_SetEnable()
Run($remoteplay)
Local $hWnd = WinWait($win_title,$btn_start,120)
If $hWnd == 0 Then
   _log4a_Info("Open PS4 remote timeout")
   Exit
EndIf

_log4a_Info("PS4 remote started.")
Sleep(1*1000)
; press start
ControlClick($hWnd, "",$btn_start)
Sleep(20*1000)

$hBitmap = _ScreenCapture_CaptureWnd("", $hWnd)
_ScreenCapture_SaveImage(@MyDocumentsDir & "\GDIPlus_Image.jpg",$hBitmap)

_log4a_Info("Start to play games")

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





