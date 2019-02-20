#AutoIt3Wrapper_UseX64=n ; In order for the x86 DLLs to work
#include-once
#include <Timers.au3>
#include <ScreenCapture.au3>
#include <GUIConstantsEx.au3>
#include <ImageSearch.au3>
#include "log4a.au3"
#include "OpenCV-Match_UDF.au3"


Global $remoteplay = "C:\Program Files (x86)\Sony\PS4 Remote Play\RemotePlay.exe"
Global $rplay_class = "WindowsForms10.BUTTON.app.0.141b42a_r9_ad1"
Global $btn_start = "开始"
Global $win_title = "PS4遥控操作"

_OpenCV_Startup();loads opencv DLLs
_OpenCV_EnableLogging(True,True,True) ;Logs matches, errors in a log file and autoit console output.
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

Local $Threshold = 0.3
While 1
   if not WinExists($win_title) Then
	  _log4a_Info("The window is closed")
	  ExitLoop
   EndIf

   ;$hBitmap = _ScreenCapture_CaptureWnd("", $hWnd)
   ;_ScreenCapture_SaveImage(@MyDocumentsDir&"\test_folder\"&@HOUR&@MIN&@SEC&"Image.jpg", $hBitmap)

   $Match = _MatchPicture(@ScriptDir&"\pes2019_img_search\start_game.png", $Threshold)
   If Not @error Then
	  _log4a_Info("find start game pic")
	  Send("{ENTER}")
	  Sleep(1*1000)
	  ContinueLoop
   EndIf


   $Match = _MatchPicture(@ScriptDir&"\pes2019_img_search\pause_menu.png", $Threshold)
   If Not @error Then
	  _log4a_Info("find use select menu")
	  Send("{ESC}")
	  Sleep(1*1000)
	  ContinueLoop
   EndIf

   $Match = _MatchPicture(@ScriptDir&"\pes2019_img_search\pause_menu_2.png", $Threshold)
   If Not @error Then
	  _log4a_Info("find pause menu")
	  Send("{ESC}")
	  Sleep(1*1000)
	  ContinueLoop
   EndIf

   $Match = _MatchPicture(@ScriptDir&"\pes2019_img_search\match_end.png", $Threshold)
   If Not @error Then
	  _log4a_Info("find match end stage")
	  Send("{ENTER}")
	  Sleep(1*1000)
	  ContinueLoop
   EndIf

   $Match = _MatchPicture(@ScriptDir&"\pes2019_img_search\match_end_continue.png", $Threshold)
   If Not @error Then
	  _log4a_Info("find match end continue icon")
	  Send("{ENTER}")
	  Sleep(1*1000)
	  ContinueLoop
   EndIf




   Sleep(2*1000)
WEnd

_OpenCV_Shutdown();Closes DLLs


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




