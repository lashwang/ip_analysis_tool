#AutoIt3Wrapper_UseX64=n ; In order for the x86 DLLs to work
#include-once
#include "log4a.au3"


_log4a_SetEnable()
checkInvalidWindow()

Func checkInvalidWindow()
    Local $tv_title = "发起会话"
    Local $tv_btn = "确定"
    Local $tv_Wnd = WinExists($tv_title,$tv_btn)
    If $tv_Wnd Then
	  _log4a_Info("Find team view window")
	  $tv_Wnd = WinActivate($tv_title)
	  WinWaitActive($tv_title,"",10)
	  ControlClick($tv_Wnd, "",$tv_btn)
      return
    EndIf
EndFunc