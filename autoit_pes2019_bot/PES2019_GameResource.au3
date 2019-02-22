#AutoIt3Wrapper_UseX64=n ; In order for the x86 DLLs to work
#include-once
#include "log4a.au3"
#include "OpenCV-Match_UDF.au3"
#include "PS4_KeyAPI.au3"

Global const $g_IMG_HIGHLIGHT_YES               = 1
Global const $g_IMG_HIGHLIGHT_NO                = 2
Global const $g_IMG_START_GAME                  = 3
Global const $g_IMG_USER_SELECT_MENU            = 4
Global const $g_IMG_HALF_TIME                   = 5
Global const $g_IMG_PAUSE_MENU                  = 6
Global const $g_IMG_MATCH_END                   = 7
Global const $g_IMG_TEAM_MANAGER_ITEM           = 8
Global const $g_IMG_TEAM_MANAGER_MAIN           = 9
Global const $g_IMG_RECONTRACT_MANGER_NOTIFY    = 10
Global const $g_IMG_RENEW_CONTRACT_SUCCESS      = 11
Global const $g_IMG_GAME_REPLAY                 = 12
Global const $g_IMG_GAME_REPLAY_2               = 13
Global const $g_IMG_NUM_MAX = 100


Global $g_GAME_PIC_ARRAY[$g_IMG_NUM_MAX]

if @ScriptName == "PES2019_GameResource.au3" then
    _log4a_SetEnable()
    _GameResource_Startup()
endif



Func _GameResource_Startup()
    For $i = 0 To UBound($g_GAME_PIC_ARRAY) - 1
        $g_GAME_PIC_ARRAY[$i] = ""
    next
    $g_GAME_PIC_ARRAY[$g_IMG_HIGHLIGHT_YES] = "highlight_yes.png"
    $g_GAME_PIC_ARRAY[$g_IMG_HIGHLIGHT_NO] = "highlight_no.png"
    $g_GAME_PIC_ARRAY[$g_IMG_START_GAME] = "start_game.png"
    $g_GAME_PIC_ARRAY[$g_IMG_USER_SELECT_MENU] = "user_select_menu.png"
    $g_GAME_PIC_ARRAY[$g_IMG_HALF_TIME] = "half_time.png"
    $g_GAME_PIC_ARRAY[$g_IMG_PAUSE_MENU] = "pause_menu.png"
    $g_GAME_PIC_ARRAY[$g_IMG_MATCH_END] = "match_end.png"
    $g_GAME_PIC_ARRAY[$g_IMG_TEAM_MANAGER_ITEM] = "team_manager_item.png"
    $g_GAME_PIC_ARRAY[$g_IMG_TEAM_MANAGER_MAIN] = "team_manager_main.png"
    $g_GAME_PIC_ARRAY[$g_IMG_RECONTRACT_MANGER_NOTIFY] = "recontract_manger_notify.png"
    $g_GAME_PIC_ARRAY[$g_IMG_RENEW_CONTRACT_SUCCESS] = "renew_contract_success.png"
    $g_GAME_PIC_ARRAY[$g_IMG_GAME_REPLAY] = "game_replay.png"
    $g_GAME_PIC_ARRAY[$g_IMG_GAME_REPLAY_2] = "game_replay_2.png"
    
EndFunc


Func CheckGameState($hBitmap,$Threshold,$onMatched)
    For $i = 0 To UBound($g_GAME_PIC_ARRAY) - 1
        $pic_name = $g_GAME_PIC_ARRAY[$i]
        if $pic_name == "" then
            ContinueLoop
        endif
        ; Do Pic match compare
        $Match_Pic = @ScriptDir&"\pes2019_img_search\"&$pic_name
        $Match = _MatchPicture($Match_Pic,$hBitmap, $Threshold)
        If Not @error Then
            ;Find match pic
            _log4a_Info("match success for "&$pic_name)
            if $i == $g_IMG_GAME_REPLAY or $i == $g_IMG_GAME_REPLAY_2 then
                _KeyPress($g_KEY_ID_OPTION)
            endif 
            call($onMatched,$i,$hBitmap)
        else
            ;_log4a_Info("match faied for "&$pic_name)
        EndIf
    next


EndFunc



