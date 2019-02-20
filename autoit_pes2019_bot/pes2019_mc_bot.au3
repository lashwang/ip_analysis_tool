#AutoIt3Wrapper_UseX64=n ; In order for the x86 DLLs to work
#include-once
#include <Timers.au3>
#include <ScreenCapture.au3>
#include <GUIConstantsEx.au3>
#include <ImageSearch.au3>
#include "log4a.au3"
#include "OpenCV-Match_UDF.au3"
#include <Array.au3>
#include <StringConstants.au3>
#include "authread.au3"





Global $remoteplay = "C:\Program Files (x86)\Sony\PS4 Remote Play\RemotePlay.exe"
Global $process_name = "RemotePlay.exe"
Global $rplay_class = "WindowsForms10.BUTTON.app.0.141b42a_r9_ad1"
Global $btn_start = "开始"
Global $win_title = "PS4遥控操作"
Global $game_window_check_time = 2*1000
Global $STATE_CHECK_WIN_CLOSED = 1
Global $STATE_CHECK_MATCHED = 2
Global $STATE_CHECK_NOT_MATCHED = 3

_log4a_SetEnable()

If ProcessExists($process_name) Then ; Check if the Notepad process is running.
    _log4a_Info("process already existed.")
	exit 0
 EndIf



_OpenCV_Startup();loads opencv DLLs
;_OpenCV_EnableLogging(True,True,True) ;Logs matches, errors in a log file and autoit console output.
;_AuThread_Startup()


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

Local $Threshold = 0.7
Global $game_pic_array[0]
_ArrayAdd($game_pic_array, "start_game.png")
_ArrayAdd($game_pic_array, "user_select_menu.png")
_ArrayAdd($game_pic_array, "pause_menu.png")
_ArrayAdd($game_pic_array, "match_end.png")
_ArrayAdd($game_pic_array, "match_end_continue.png")



While(1)
    Local $hBitmap = _ScreenCapture_CaptureWnd("", $hWnd)

    For $i = 0 To UBound($game_pic_array) - 1
        $ret = CheckGameState($game_pic_array[$i],$hBitmap,$Threshold)
        if $ret == $STATE_CHECK_WIN_CLOSED Then
            _WinAPI_DeleteObject($hBitmap)
            ExitLoop 2
        endif

        if $ret == $STATE_CHECK_MATCHED Then
            DoKeyPress($i)
            _WinAPI_DeleteObject($hBitmap)
            Sleep($game_window_check_time)
            ContinueLoop 2
        endif
    next

    ;_ScreenCapture_SaveImage(@MyDocumentsDir&"\test_folder\"&@HOUR&@MIN&@SEC&"Image.jpg", $hBitmap)
    _WinAPI_DeleteObject($hBitmap)
    Sleep($game_window_check_time)
WEnd

_OpenCV_Shutdown();Closes DLLs





Func CheckGameState($pic_name,$hBitmap,$Threshold)
    $Match_Pic = @ScriptDir&"\pes2019_img_search\"&$pic_name

    ; Check win status
	if not WinExists($win_title) Then
		_log4a_Info("The window is closed")
		return $STATE_CHECK_WIN_CLOSED
	EndIf

    ; Do Pic match compare
	$Match = _MatchPicture($Match_Pic,$hBitmap, $Threshold)
    If Not @error Then
        ;Find match pic
        _log4a_Info("match success for "&$pic_name)
        return $STATE_CHECK_MATCHED
    else
        ;_log4a_Info("match faied for "&$pic_name)
        return $STATE_CHECK_NOT_MATCHED
    EndIf
EndFunc


Func DoKeyPress($arry_index)
    Switch $arry_index
        case 0
            SendEnter()
        case 1
            SendESC()
            SendESC()
            SendESC()
        case 2
            SendESC()
        case 3
            SendEnter()
        case 4
            SendEnter()
    EndSwitch

EndFunc


Func SendEnter()
    Send("{ENTER}")
    WinWait($win_title, "", 10)
    _log4a_Info("sending {ENTER}")
EndFunc


Func SendESC()
    Send("{ESC}")
    WinWait($win_title, "", 10)
    _log4a_Info("sending {ESC}")
EndFunc

