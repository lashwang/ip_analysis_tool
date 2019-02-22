#AutoIt3Wrapper_UseX64=n ; In order for the x86 DLLs to work
#include-once
#include <Timers.au3>
#include <ScreenCapture.au3>
#include <GUIConstantsEx.au3>
;#include <ImageSearch.au3>
#include "log4a.au3"
#include "OpenCV-Match_UDF.au3"
#include <Array.au3>
#include <StringConstants.au3>
#include "PS4_RPLAY_CONST.au3"
#include "PS4_KeyAPI.au3"
#include "Utils.au3"
#include "PS4_Rplay_GameWindow.au3"
#include "PES2019_GameResource.au3"

Global $game_window_check_time = 1*1000
Global $match_end_processing = False
Global $email_sent = False
Global $find_manager_renew_screen = False
Global $g_log_path = @MyDocumentsDir&"\pes2019.log"
Global $g_game_end_snapshot = @MyDocumentsDir&"\pes2019_game_finish.jpg"

DirCreate(@MyDocumentsDir & "\test_folder\")

_log4a_SetEnable()
_log4a_SetLogFile($g_log_path)
_log4a_SetOutput($LOG4A_OUTPUT_BOTH)
_KeyMap_Startup()
_OpenCV_Startup();loads opencv DLLs
_PS4_GameWindow_StartUp()

_log4a_Info("Start to play games")

_GameResource_Startup()
Local $Threshold = 0.7

Func DoKeyPress($arry_index,$hBitmap)
	_log4a_Info("DoKeyPress:"&$arry_index)
    Switch $arry_index
         case $g_IMG_START_GAME ;start game window
            _KeyPress($g_KEY_ID_CIRCLE)
         case $g_IMG_USER_SELECT_MENU ;手柄选择界面
            _KeyPress($g_KEY_ID_CROSS)
	     case $g_IMG_HALF_TIME ;中场休息
			_KeyPress($g_KEY_ID_CIRCLE)
         case $g_IMG_PAUSE_MENU ;暂停界面
            _KeyPress($g_KEY_ID_CROSS)
         case $g_IMG_MATCH_END ;比赛结束界面
			_ScreenCapture_SaveImage($g_game_end_snapshot,$hBitmap)
			_KeyPress($g_KEY_ID_CIRCLE)
			_KeyPress($g_KEY_ID_CIRCLE)
			_KeyPress($g_KEY_ID_CIRCLE)
			_KeyPress($g_KEY_ID_CIRCLE)
			_KeyPress($g_KEY_ID_CIRCLE)
            send_email($g_log_path&";"&$g_game_end_snapshot)
			sleep(1000)
            ProcessClose($g_RPLAY_EXE)
            ProcessClose($g_PS4Macro_EXE)
		 case $g_IMG_TEAM_MANAGER_ITEM ;小队管理菜单
            
         case $g_IMG_TEAM_MANAGER_MAIN ;小队管理主界面
            AdlibUnRegister("processMatchEnd")
            $match_end_processing = False
            _KeyPress($g_KEY_ID_CROSS)
         case $g_IMG_RECONTRACT_MANGER_NOTIFY ;主教练续约
            if not $find_manager_renew_screen then
                $find_manager_renew_screen = True
            endif
         case $g_IMG_HIGHLIGHT_YES ;yes
            if $find_manager_renew_screen then
                _KeyPress($g_KEY_ID_CIRCLE)
                AdlibRegister("processManagerRecontract",1*1000)
            endif
         case $g_IMG_HIGHLIGHT_NO ;no
            if $find_manager_renew_screen then
                _KeyPress($g_KEY_ID_RIGHT)
            endif
         case $g_IMG_RECONTRACT_MANGER_NOTIFY ;已延长合约
            if $find_manager_renew_screen then
                $find_manager_renew_screen = False
                AdlibUnRegister("processManagerRecontract")
            endif
    EndSwitch
EndFunc

While(1)
    If not ProcessExists($g_RPLAY_EXE) Then
		_log4a_Info("Process exited,stop!!!!")
		exit 0
	endif
    ; if not WinActive($g_RPLAY_WIN_TITLE) then
        ; _log4a_Info("win is not active, skip game state check")
        ; Sleep($game_window_check_time)
        ; ContinueLoop
    ; endif
    Local $hBitmap = _ScreenCapture_CaptureWnd("", $g_hwnd_rplay)
    CheckGameState($hBitmap,$Threshold,"DoKeyPress")
    _WinAPI_DeleteObject($hBitmap)
    Sleep($game_window_check_time)
WEnd

_OpenCV_Shutdown();Closes DLLs

Func processMatchEnd()
    if $match_end_processing then
        if not $find_manager_renew_screen then
            _log4a_Info("processMatchEnd")
            _KeyPress($g_KEY_ID_CIRCLE)
        endif
    endif
EndFunc

Func processManagerRecontract()
    if $find_manager_renew_screen then
        _log4a_Info("processManagerRecontract")
        _KeyPress($g_KEY_ID_CIRCLE)
    endif
EndFunc





