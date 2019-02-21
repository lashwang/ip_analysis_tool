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
#include "authread.au3"
#include "SmtpMailer.au3"




Global $remoteplay = "C:\Program Files (x86)\Sony\PS4 Remote Play\RemotePlay.exe"
Global $process_name = "RemotePlay.exe"
Global $rplay_class = "WindowsForms10.BUTTON.app.0.141b42a_r9_ad1"
Global $btn_start = "开始"
Global $win_title = "PS4遥控操作"
Global $game_window_check_time = 2*1000
Global $STATE_CHECK_WIN_CLOSED = 1
Global $STATE_CHECK_MATCHED = 2
Global $STATE_CHECK_NOT_MATCHED = 3
Global $game_window_started = False
Global $match_end_processing = False
Global $email_sent = False
Global $find_manager_renew_screen = False
Global $current_game_index = 0

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

AdlibRegister("ProcessCheck",1*1000)
AdlibRegister("onViewPanelCheck",5*1000)
AdlibRegister("screen_capture",20*1000)



While (not $game_window_started)
   Sleep(2*1000)
WEnd

AdlibUnRegister("onViewPanelCheck")

WinActive($win_title)
Sleep(1*1000)
$hWnd = WinWaitActive($win_title,"",120)
_log4a_Info("Start to play games")

Local $Threshold = 0.7
Global $game_pic_array[0]
_ArrayAdd($game_pic_array, "start_game.png") 			;0
_ArrayAdd($game_pic_array, "user_select_menu.png")		;1
_ArrayAdd($game_pic_array, "half_time.png")				;2
_ArrayAdd($game_pic_array, "pause_menu.png")			;3
_ArrayAdd($game_pic_array, "match_end.png")				;4
_ArrayAdd($game_pic_array, "team_manager_item.png")		;5
_ArrayAdd($game_pic_array, "team_manager_main.png")		;6
_ArrayAdd($game_pic_array, "recontract_manger_notify.png")		    ;7
_ArrayAdd($game_pic_array, "highlight_yes.png")		                ;8
_ArrayAdd($game_pic_array, "highlight_no.png")		                ;9
_ArrayAdd($game_pic_array, "renew_contract_success.png")		    ;10


Func DoKeyPress($arry_index,$hBitmap)
    Switch $arry_index
         case 0 ;start game window
            SendEnter()
            SendEnter()
            SendEnter()
			AdlibRegister("screen_capture",60*1000)
         case 1 ;手柄选择界面
            SendESC()
            SendESC()
            SendESC()
			AdlibRegister("screen_capture",60*1000)
	     case 2 ;中场休息
			SendEnter()
            SendEnter()
         case 3 ;暂停界面
            SendESC()
         case 4 ;比赛结束界面
            SendEnter()
            $match_end_processing = True
			$email_sent = False
			AdlibRegister("screen_capture",2*1000)
            AdlibRegister("processMatchEnd",5*1000)
		 case 5 ;小队管理菜单
            AdlibUnRegister("processMatchEnd")
            $match_end_processing = False
			if not $email_sent then
				send_email()
				$email_sent = True
			endif
         case 6 ;小队管理主界面
            AdlibUnRegister("processMatchEnd")
            $match_end_processing = False
            SendESC()
         case 7 ;主教练续约
            if not $find_manager_renew_screen then
                $find_manager_renew_screen = True
            endif
         case 8 ;yes
            if $find_manager_renew_screen then
                SendEnter()
                AdlibRegister("processManagerRecontract",1*1000)
            endif
         case 9 ;no
            if $find_manager_renew_screen then
                SendRight()
            endif
         case 10 ; 已延长合约
            if $find_manager_renew_screen then
                $find_manager_renew_screen = False
                AdlibUnRegister("processManagerRecontract")
            endif
    EndSwitch
EndFunc

While(1)
    Local $hBitmap = _ScreenCapture_CaptureWnd("", $hWnd)

    For $i = 0 To UBound($game_pic_array) - 1
        $ret = CheckGameState($game_pic_array[$i],$hBitmap,$Threshold)
        if $ret == $STATE_CHECK_WIN_CLOSED Then
            _WinAPI_DeleteObject($hBitmap)
            ExitLoop 2
        endif

        if $ret == $STATE_CHECK_MATCHED Then
            activatePlayWindow()
            DoKeyPress($i,$hBitmap)
            $current_game_index = $i
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





Func SendEnter()
    Send("{ENTER}")
    WinWait($win_title, "", 100)
    _log4a_Info("sending {ENTER}")
EndFunc


Func SendESC()
    Send("{ESC}")
    WinWait($win_title, "", 100)
    _log4a_Info("sending {ESC}")
EndFunc

Func SendRight()
    send("{RIGHT}")
    WinWait($win_title, "", 100)
    _log4a_Info("sending {RIGHT}")
EndFunc

Func ProcessCheck()
	;_log4a_Info("ProcessCheck")
	If not ProcessExists($process_name) Then
		_log4a_Info("Process exited,stop!!!!")
		exit 0
	endif
    checkInvalidWindow()
EndFunc


Func onViewPanelCheck()
	_log4a_Info("onViewPanelCheck");
	If not $game_window_started And WinExists($win_title) Then
		$hCtrl = ControlGetHandle($win_title, "", "[NAME:ViewPanel]")
		If $hCtrl Then
			; we got the handle, so the button is there
			; now do whatever you need to do
			_log4a_Info("Find Viewpanel!!!");
			$game_window_started = True
		EndIf
	EndIf
EndFunc

Func screen_capture()
	;Local $hBitmap = _ScreenCapture_CaptureWnd("", $hWnd)
	;_ScreenCapture_SaveImage(@MyDocumentsDir&"\test_folder\image_"&@HOUR&"_"&@MIN&"_"&@SEC&".bmp", $hBitmap)
	;_WinAPI_DeleteObject($hBitmap)
EndFunc


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


Func processMatchEnd()
    if $match_end_processing then
        if not $find_manager_renew_screen then
            _log4a_Info("processMatchEnd")
            activatePlayWindow()
            SendEnter()
        endif
    endif
EndFunc

Func processManagerRecontract()
    if $find_manager_renew_screen then
        _log4a_Info("processManagerRecontract")
        activatePlayWindow()
        SendEnter()
    endif
EndFunc

Func activatePlayWindow()
    WinActivate($win_title)
	WinWaitActive($win_title,"",1)
EndFunc


Func send_email()
    Local $sSmtpServer = "smtp.ym.163.com" ; address for the smtp-server to use - REQUIRED
	Local $iIPPort = 994 ; port used for sending the mail
    Local $sFromName = "Simon" ; name from who the email was sent
    Local $sFromAddress = "stock@zl-fm.com" ; address from where the mail should come
    Local $sToAddress = "lashwang@outlook.com" ; destination address of the email - REQUIRED
	Local $sCcAddress = "" ; address for cc - leave blank if not needed
    Local $sSubject = "PES2019 Game Finished" ; subject from the email - can be anything you want it to be
    Local $sBody = "PES2019 Game Finished" ; the messagebody from the mail - can be left blank but then you get a blank mail
    Local $sAttachFiles = "" ; the file(s) you want to attach seperated with a ; (Semicolon) - leave blank if not needed
    Local $sBccAddress = "" ; address for bcc - leave blank if not needed
    Local $sImportance = "Normal" ; Send message priority: "High", "Normal", "Low"
    Local $sUsername = "stock@zl-fm.com" ; username for the account used from where the mail gets sent - REQUIRED
    Local $sPassword = "992154" ; password for the account used from where the mail gets sent - REQUIRED
    Local $bSSL = True ; enables/disables secure socket layer sending - set to True if using httpS
    ; Local $iIPPort = 465  ; GMAIL port used for sending the mail
    ; Local $bSSL = True   ; GMAIL enables/disables secure socket layer sending - set to True if using httpS

    Local $bIsHTMLBody = False

    Local $rc = _SMTP_SendEmail($sSmtpServer,$sUsername, $sPassword, $sFromName, $sFromAddress, $sToAddress, $sSubject, $sBody, $sAttachFiles, $sCcAddress, $sBccAddress, $sImportance,  $iIPPort, $bSSL, $bIsHTMLBody)
    If @error Then
        _log4a_Info("send email failed."&@extended);
    EndIf

EndFunc   ;==>_Example