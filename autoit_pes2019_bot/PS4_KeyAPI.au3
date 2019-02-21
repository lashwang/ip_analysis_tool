#AutoIt3Wrapper_UseX64=n ; In order for the x86 DLLs to work
#include-once
#include "log4a.au3"
#include "PS4_RPLAY_CONST.au3"

Global $g_KEY_ID_NONE        = 0
Global $g_KEY_ID_CROSS       = 1
Global $g_KEY_ID_TRIANGLE    = 2
Global $g_KEY_ID_SQUARE      = 3
Global $g_KEY_ID_CIRCLE      = 4
Global $g_KEY_ID_UP          = 5
Global $g_KEY_ID_DOWN        = 6
Global $g_KEY_ID_LEFT        = 7
Global $g_KEY_ID_RIGHT       = 8
Global $g_KEY_ID_OPTION      = 9
Global $g_KEY_ID_PS          = 10
Global $g_KEY_ID_L1          = 11
Global $g_KEY_ID_R1          = 12
Global $g_KEY_ID_L2          = 13
Global $g_KEY_ID_R2          = 14
Global const $g_KEY_ID_MAX   = 20
Global const $g_DEFAULT_KEYDOWN_DELAY = 80

Global $g_KEY_MAP[$g_KEY_ID_MAX]

if @ScriptName == "PS4_KeyAPI.au3" then
    _KeyMap_Startup()
    test_ps4_key_map()
endif

Func test_ps4_key_map()
    _log4a_SetEnable()
    _log4a_Info(@ScriptName)
    While True
        _KeyPress($g_KEY_ID_PS)
        Sleep(5000)
    WEnd
EndFunc

Func _KeyMap_Startup()
    _log4a_Info("_KeyMap_Startup")
    Opt('SendKeyDownDelay',$g_DEFAULT_KEYDOWN_DELAY)
    
    $g_KEY_MAP[$g_KEY_ID_OPTION] = "{Z}"
    $g_KEY_MAP[$g_KEY_ID_PS] = "{LSHIFT}"


    $g_KEY_MAP[$g_KEY_ID_TRIANGLE] = "{C}"
    $g_KEY_MAP[$g_KEY_ID_CIRCLE] = "{ENTER}"
    $g_KEY_MAP[$g_KEY_ID_CROSS] = "{ESCAPE}"
    $g_KEY_MAP[$g_KEY_ID_SQUARE] = "{V}"

    $g_KEY_MAP[$g_KEY_ID_UP] = "{UP}"
    $g_KEY_MAP[$g_KEY_ID_DOWN] = "{DOWN}"
    $g_KEY_MAP[$g_KEY_ID_LEFT] = "{LEFT}"
    $g_KEY_MAP[$g_KEY_ID_RIGHT] = "{RIGHT}"

    $g_KEY_MAP[$g_KEY_ID_L1] = "{Q}"
    $g_KEY_MAP[$g_KEY_ID_R1] = "{E}"
    $g_KEY_MAP[$g_KEY_ID_L2] = "{U}"
    $g_KEY_MAP[$g_KEY_ID_R2] = "{O}"

    
EndFunc


Func _KeyPress($key_id)
    $key_name = $g_KEY_MAP[$key_id]
    WinActivate($g_RPLAY_WIN_TITLE)
    Sleep(100)
	_log4a_Info("KeyPress:"&$key_name)
    ;ControlSend($g_RPLAY_WIN_TITLE,"","",$key_name)
	Send($key_name)
EndFunc
