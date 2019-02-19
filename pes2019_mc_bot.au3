#include-once
#include <Timers.au3>
#include "log4a.au3"


$remoteplay = "C:\Program Files (x86)\Sony\PS4 Remote Play\RemotePlay.exe"
$rplay_class = "WindowsForms10.BUTTON.app.0.141b42a_r9_ad1"
$btn_start = "开始"


_log4a_SetEnable()
Run($remoteplay)
Local $hWnd = WinWait("PS4遥控操作",$btn_start,20)
If $hWnd == 0 Then
   _log4a_Info("Open PS4 remote timeout")
   Exit
 EndIf

_log4a_Info("PS4 remote started.")
Sleep(1)
;
ControlClick($hWnd, "",$btn_start)
Sleep(1)
