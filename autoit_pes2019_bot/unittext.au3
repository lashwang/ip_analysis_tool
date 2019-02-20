#AutoIt3Wrapper_UseX64=n ; In order for the x86 DLLs to work
#include-once
#include "log4a.au3"
#include "SmtpMailer.au3"


_log4a_SetEnable()
checkInvalidWindow()
send_email()


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

Func send_email()
    Local $sSmtpServer = "smtp-mail.outlook.com" ; address for the smtp-server to use - REQUIRED
    Local $sFromName = "Simon" ; name from who the email was sent
    Local $sFromAddress = "lashwang@outlook.com" ; address from where the mail should come
    Local $sToAddress = "lashwang@outlook.com" ; destination address of the email - REQUIRED
    Local $sSubject = "Email sent from autoit" ; subject from the email - can be anything you want it to be
    Local $sBody = "Email sent from autoit" ; the messagebody from the mail - can be left blank but then you get a blank mail
    Local $sAttachFiles = "" ; the file(s) you want to attach seperated with a ; (Semicolon) - leave blank if not needed
    Local $sCcAddress = "" ; address for cc - leave blank if not needed
    Local $sBccAddress = "" ; address for bcc - leave blank if not needed
    Local $sImportance = "Normal" ; Send message priority: "High", "Normal", "Low"
    Local $sUsername = "lashwang@outlook.com" ; username for the account used from where the mail gets sent - REQUIRED
    Local $sPassword = "meimei1985" ; password for the account used from where the mail gets sent - REQUIRED
    Local $iIPPort = 587 ; port used for sending the mail
    Local $bSSL = True ; enables/disables secure socket layer sending - set to True if using httpS
    ; Local $iIPPort = 465  ; GMAIL port used for sending the mail
    ; Local $bSSL = True   ; GMAIL enables/disables secure socket layer sending - set to True if using httpS

    Local $bIsHTMLBody = False

    Local $rc = _SMTP_SendEmail($sSmtpServer, $sFromName, $sFromAddress, $sToAddress, $sSubject, $sBody, $sAttachFiles, $sCcAddress, $sBccAddress, $sImportance, $sUsername, $sPassword, $iIPPort, $bSSL, $bIsHTMLBody)
    If @error Then
        _log4a_Info("send email failed."&@extended);
    EndIf

EndFunc   ;==>_Example