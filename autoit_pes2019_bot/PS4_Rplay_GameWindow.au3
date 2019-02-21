#AutoIt3Wrapper_UseX64=n ; In order for the x86 DLLs to work
#include-once
#include "PS4_RPLAY_CONST.au3"
#include "log4a.au3"
#include "Utils.au3"


Global $g_hwnd_rplay = 0
Global $g_rplay_started = False
Global const $g_WindowPosX = 175
Global const $g_WindowPosY = 35
Global const $g_WindowWidth = 883
Global const $g_WindowHight = 583

if @ScriptName == "PS4_Rplay_GameWindow.au3" then
    _log4a_SetEnable()
    _PS4_GameWindow_StartUp()
endif


Func _PS4_GameWindow_StartUp()
    if Not WinExists($g_RPLAY_WIN_TITLE) Then
        Sleep(2000)
    endif

    ;如果RPLAY已经打开了
    If Not ProcessExists($g_RPLAY_EXE) Then
        Run($g_RPLAY_EXE_PATH)
        $hWnd = WinWaitActive($g_RPLAY_WIN_TITLE,$g_RPLAY_BTN_START,120)
        If $hWnd == 0 Then
            _log4a_Info("Open PS4 remote timeout")
            Exit 0
        EndIf
    EndIf

    _log4a_Info("PS4 Game Window Starting")

    AdlibRegister("GameWindowCheck",5*1000)

    If WinExists($g_RPLAY_WIN_TITLE,$g_RPLAY_BTN_START) Then
		$hWnd = WinActivate($g_RPLAY_WIN_TITLE)
        Sleep(1*1000)
        _log4a_Info("Waiting for the start button press")
        ControlClick($hWnd, "",$g_RPLAY_BTN_START)
        Sleep(1*1000)
    endif

    $hCtrl = ControlGetHandle($g_RPLAY_WIN_TITLE, "", $g_RPLAY_GAME_CONTROL_CLASS)
    If Not $hCtrl Then
        AdlibRegister("onViewPanelCheck",1*1000)
        While not $g_rplay_started
            Sleep(1*1000)
        WEnd
        AdlibUnRegister("onViewPanelCheck")
    Endif
    $g_rplay_started = True

    WinActivate($g_RPLAY_WIN_TITLE)
    $g_hwnd_rplay = WinWaitActive($g_RPLAY_WIN_TITLE,"",120)
    _log4a_Info("PS4 Game Window Start compelete,hwnd="&$g_hwnd_rplay)
    WinMove($g_RPLAY_WIN_TITLE,"",$g_WindowPosX,$g_WindowPosY,$g_WindowWidth,$g_WindowHight)
EndFunc

Func onViewPanelCheck()
	_log4a_Info("onViewPanelCheck");
	If not $g_rplay_started And WinExists($g_RPLAY_WIN_TITLE) Then
		$hCtrl = ControlGetHandle($g_RPLAY_WIN_TITLE, "", $g_RPLAY_GAME_CONTROL_CLASS)
		If $hCtrl Then
			; we got the handle, so the button is there
			; now do whatever you need to do
			_log4a_Info("Find Viewpanel!!!");
			$g_rplay_started = True
		EndIf
	EndIf
EndFunc


Func GameWindowCheck()
    If not ProcessExists($g_RPLAY_EXE) Then
		_log4a_Info("Process exited,stop!!!!")
		exit 0
	endif
    checkInvalidWindow()
    WinActivate($g_RPLAY_WIN_TITLE)
    Local $aPos = WinGetPos($g_RPLAY_WIN_TITLE)
    ;_log4a_Info("X-Pos: "&$aPos[0]&"Y-Pos: "&$aPos[1]&"Width: "&$aPos[2]&"Height: "&$aPos[3])
    
    WinMove($g_RPLAY_WIN_TITLE,"",$aPos[0],$aPos[1],$g_WindowWidth,$g_WindowHight)
EndFunc


