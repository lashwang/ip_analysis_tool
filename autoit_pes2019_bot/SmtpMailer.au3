#AutoIt3Wrapper_Au3Check_Parameters=-d -w 1 -w 2 -w 3 -w 4 -w 5 -w 6 -w 7
;~ #AutoIt3Wrapper_Run_Debug_Mode=Y                 ;(Y/N) Run Script with console debugging. Default=N

#Region IE.au3 - Header

; #INDEX# =======================================================================================================================
; Title .........: SMTP UDF Library for AutoIt3
; AutoIt Version : 3.3.14.x
; Language ......: English
; Description ...: Function for sending emails
; Author(s) .....: Jos, mLipok
; ===============================================================================================================================

#CS
	This is modified version of Jos "Smtp Mailer That Supports Html And Attachments"
	https://www.autoitscript.com/forum/topic/23860-smtp-mailer-that-supports-html-and-attachments/

	Update History:

	>>>>> 2015/02/05
	- First release - mLipok

	>>>>> 2015/02/13
	- New: Function: _SMTP_SaveMessageToFile - mLipok
	-		https://www.autoitscript.com/forum/topic/167292-smtp-mailer-udf/?do=findComment&comment=1225420

	>>>>> 2016/01/31
	- Renamed: Enums: $g__INetSmtpMailCom_ERROR_ .... >>  $SMTP_ERR_ .... - mLipok
	- New: Enum: $SMTP_ERR_SUCCESS - mLipok
	- Changed: concept of COM Error Handling - mLipok
	- Removed: Function: _INetSmtpMailCom_ErrObjInit - mLipok
	- Removed: Function: _INetSmtpMailCom_ErrObjCleanUp - mLipok
	- Renamed: Function: _INetSmtpMailCom >> _SMTP_SendEmail - mLipok
	- Renamed: Function: _INetSmtpMailCom_ErrFunc >> _SMTP_COMErrorHexNumber - mLipok
	- Renamed: Function: _INetSmtpMailCom_ErrDescription >> _SMTP_COMErrorDescription - mLipok
	- Renamed: Function: _INetSmtpMailCom_ErrScriptLine >> _SMTP_COMErrorScriptLine - mLipok
	- Renamed: Function: _INetSmtpMailCom_ErrFunc >> __SMTP_COMErrorFunc - mLipok
	- Changed: Function: __SMTP_COMErrorFunc is now UDF's Internal Function - mLipok
	- New: Function Parameter: $sCharset in  _SMTP_SaveMessageToFile  - mLipok
	- Changed: Function: _SMTP_SendEmail - paramters are reordered - mLipok

	@LAST
#CE
#EndRegion  IE.au3 - Header

#Region INCLUDE
;##################################
; Include
;##################################
#include <file.au3>
#EndRegion  INCLUDE

#Region Variables
;##################################
; Variables
;##################################
Global Enum _
		$SMTP_ERR_SUCCESS, _
		$SMTP_ERR_FILENOTFOUND, _
		$SMTP_ERR_SEND, _
		$SMTP_ERR_OBJECTCREATION, _
		$SMTP_ERR_COUNTER

Global Const $g__cdoSendUsingPickup = 1 ; Send message using the local SMTP service pickup directory.
Global Const $g__cdoSendUsingPort = 2 ; Send the message using the network (SMTP over the network). Must use this to use Delivery Notification

Global Const $g__cdoAnonymous = 0 ; Do not authenticate
Global Const $g__cdoBasic = 1 ; basic (clear-text) authentication
Global Const $g__cdoNTLM = 2 ; NTLM

; Delivery Status Notifications
Global Const $g__cdoDSNDefault = 0 ; None
Global Const $g__cdoDSNNever = 1 ; None
Global Const $g__cdoDSNFailure = 2 ; Failure
Global Const $g__cdoDSNSuccess = 4 ; Success
Global Const $g__cdoDSNDelay = 8 ; Delay
Global Const $g__cdoDSNSuccessFailOrDelay = 14 ; Success, failure or delay
#EndRegion  Variables

#Region UDF Functions
; The UDF
; #FUNCTION# ====================================================================================================================
; Name ..........: _SMTP_SendEmail
; Description ...:
; Syntax ........: _SMTP_SendEmail($s_SmtpServer, $s_FromName, $s_FromAddress, $s_ToAddress[, $s_Subject = ""[, $s_Body = ""[,
;                  $s_AttachFiles = ""[, $s_CcAddress = ""[, $s_BccAddress = ""[, $s_Importance = "Normal"[, $s_Username = ""[,
;                  $s_Password = ""[, $i_IPPort = 25[, $b_SSL = False[, $b_IsHTMLBody = False[, $i_DSNOptions = $g__cdoDSNDefault]]]]]]]]]]]])
; Parameters ....: $s_SmtpServer        - A string value. Address for the smtp-server to use  - REQUIRED
;                  $s_Username          - A string value. Username for the account used from where the mail gets sent - REQUIRED
;                  $s_Password          - A string value. Password for the account used from where the mail gets sent - REQUIRED
;                  $s_FromName          - A string value. Name from who the email was sent - REQUIRED
;                  $s_FromAddress       - A string value. Address from where the mail should come - REQUIRED
;                  $s_ToAddress         - A string value. Destination email address - REQUIRED
;                  $s_Subject           - [optional] A string value. Default is "". Subject from the email - can be anything you want it to be.
;                  $s_Body              - [optional] A string value. Default is "". The messagebody from the mail - can be left blank but then you get a blank mail.
;                  $s_AttachFiles       - [optional] A string value. Default is "". The file(s) you want to attach seperated with a ; (Semicolon) - leave blank if not needed.
;                  $s_CcAddress         - [optional] A string value. Default is "". Address for cc - leave blank if not needed.
;                  $s_BccAddress        - [optional] A string value. Default is "". Address for bcc - leave blank if not needed.
;                  $s_Importance        - [optional] A string value. Default is "Normal". Send message priority: "High", "Normal", "Low".
;                  $i_IPPort            - [optional] An integer value. Default is 25. TCP Port used for sending the mail
;                  $b_SSL               - [optional] A binary value. Default is False. Enables/Disables secure socket layer sending - set to True if using https.
;                  $b_IsHTMLBody        - [optional] A binary value. Default is False.
;                  $i_DSNOptions        - [optional] An integer value. Default is $g__cdoDSNDefault.
; Return values .: None
; Author ........: Jos, mLipok
; Remarks .......: This function is based on the function created by Jos (see link in related)
; Related .......: http://www.autoitscript.com/forum/topic/23860-smtp-mailer-that-supports-html-and-attachments/
; Link ..........: http://www.autoitscript.com/forum/topic/167292-smtp-mailer-udf/
; Example .......: Yes
; ===============================================================================================================================
Func _SMTP_SendEmail($s_SmtpServer, $s_Username, $s_Password, $s_FromName, $s_FromAddress, $s_ToAddress, $s_Subject = "", $s_Body = "", $s_AttachFiles = "", $s_CcAddress = "", $s_BccAddress = "", $s_Importance = "Normal", $i_IPPort = 25, $b_SSL = False, $b_IsHTMLBody = False, $i_DSNOptions = $g__cdoDSNDefault, $sEMLPath_SaveBefore = '', $sEMLPath_SaveAfter = '')
	; Clear Error stored information
	_SMTP_COMErrorScriptLine(0)
	_SMTP_COMErrorHexNumber(0)
	_SMTP_COMErrorDescription('')

	; Initialize COM Error Handler
	Local $oSMTP_ComErrorHandler = ObjEvent("AutoIt.Error", "__SMTP_COMErrorFunc")
	#forceref $oSMTP_ComErrorHandler

	Local $oEmail = ObjCreate("CDO.Message")
	If Not IsObj($oEmail) Then Return SetError($SMTP_ERR_OBJECTCREATION, Dec(_SMTP_COMErrorHexNumber()), _SMTP_COMErrorDescription())


	$oEmail.From = '"' & $s_FromName & '" <' & $s_FromAddress & '>'
	$oEmail.To = $s_ToAddress

	If $s_CcAddress <> "" Then $oEmail.Cc = $s_CcAddress
	If $s_BccAddress <> "" Then $oEmail.Bcc = $s_BccAddress
	$oEmail.Subject = $s_Subject

	; Select whether or not the content is sent as plain text or HTM
	If $b_IsHTMLBody Then
		$oEmail.HTMLBody = $s_Body
	Else
		$oEmail.Textbody = $s_Body & @CRLF
	EndIf

	; Add Attachments
	If $s_AttachFiles <> "" Then
		Local $S_Files2Attach = StringSplit($s_AttachFiles, ";")
		For $x = 1 To $S_Files2Attach[0]
			$S_Files2Attach[$x] = _PathFull($S_Files2Attach[$x])
			If FileExists($S_Files2Attach[$x]) Then
				ConsoleWrite('+> File attachment added: ' & $S_Files2Attach[$x] & @LF)
				$oEmail.AddAttachment($S_Files2Attach[$x])
			Else
				ConsoleWrite('!> File not found to attach: ' & $S_Files2Attach[$x] & @LF)
				Return SetError($SMTP_ERR_FILENOTFOUND, 0, 0)
			EndIf
		Next
	EndIf

	; Set Email Configuration
	$oEmail.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/sendusing") = $g__cdoSendUsingPort
	$oEmail.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/smtpserver") = $s_SmtpServer
	If Number($i_IPPort) = 0 Then $i_IPPort = 25
	$oEmail.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/smtpserverport") = $i_IPPort

	;Authenticated SMTP
	If $s_Username <> "" Then
		$oEmail.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/smtpauthenticate") = $g__cdoBasic
		$oEmail.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/sendusername") = $s_Username
		$oEmail.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/sendpassword") = $s_Password
	EndIf
	$oEmail.Configuration.Fields.Item("http://schemas.microsoft.com/cdo/configuration/smtpusessl") = $b_SSL

	;Update Configuration Settings
	$oEmail.Configuration.Fields.Update

	; Set Email Importance
	Switch $s_Importance
		Case "High", "Normal", "Low"
			$oEmail.Fields.Item("urn:schemas:mailheader:Importance") = $s_Importance
		Case Else
			; TODO
	EndSwitch

	; Set DSN options
	If $i_DSNOptions <> $g__cdoDSNDefault And $i_DSNOptions <> $g__cdoDSNNever Then
		$oEmail.DSNOptions = $i_DSNOptions
		$oEmail.Fields.Item("urn:schemas:mailheader:disposition-notification-to") = $s_FromAddress
		$oEmail.Fields.Item("urn:schemas:mailheader:return-receipt-to") = $s_FromAddress
	EndIf

	; Update Importance and Options fields
	$oEmail.Fields.Update

	; Saving Message before sending
	If $sEMLPath_SaveBefore <> '' Then _SMTP_SaveMessageToFile($oEmail, $sEMLPath_SaveBefore)

	; Sent the Message
	$oEmail.Send
	If @error Then
		Return SetError($SMTP_ERR_SEND, Dec(_SMTP_COMErrorHexNumber()), _SMTP_COMErrorDescription())
	EndIf

	; Saving Message after sending
	If $sEMLPath_SaveAfter <> '' Then _SMTP_SaveMessageToFile($oEmail, $sEMLPath_SaveAfter)

	; CleanUp
	$oEmail = Null

EndFunc    ;==>_SMTP_SendEmail

; #FUNCTION# ====================================================================================================================
; Name ..........: _SMTP_SaveMessageToFile
; Description ...:
; Syntax ........: _SMTP_SaveMessageToFile(Byref $oMessage, $sFileFullPath[, $sCharset = "US-ASCII"])
; Parameters ....: $oMessage            - [in/out] an object.
;                  $sFileFullPath       - A string value.
;                  $sCharset            - [optional] a string value. Default is "US-ASCII".
; Return values .: None
; Author ........: mLipok
; Modified ......:
; Remarks .......:
; Related .......:
; Link ..........: https://msdn.microsoft.com/en-us/library/aa488396(v=exchg.65).aspx
; Example .......: No
; ===============================================================================================================================
Func _SMTP_SaveMessageToFile(ByRef $oMessage, $sFileFullPath, $sCharset = "US-ASCII")
	; Clear Error stored information
	_SMTP_COMErrorScriptLine(0)
	_SMTP_COMErrorHexNumber(0)
	_SMTP_COMErrorDescription('')

	; Initialize COM Error Handler
	Local $oSMTP_ComErrorHandler = ObjEvent("AutoIt.Error", "__SMTP_COMErrorFunc")
	#forceref $oSMTP_ComErrorHandler

	Local $oStream = ObjCreate("ADODB.Stream")
	$oStream.Open
	$oStream.Type = 2 ; adTypeText
	$oStream.Charset = $sCharset

	$oMessage.DataSource.SaveToObject($oStream, "_Stream")

	; https://msdn.microsoft.com/en-us/library/windows/desktop/ms676152(v=vs.85).aspx
	$oStream.SaveToFile($sFileFullPath, 2) ; adSaveCreateOverWrite = 2

	; CleanUp
	$oStream = Null

EndFunc    ;==>_SMTP_SaveMessageToFile
#EndRegion  UDF Functions

#Region UDF Functions - COM Error Handler
Func _SMTP_COMErrorHexNumber($vData = Default)
	Local Static $vReturn = 0
	If $vData <> Default Then $vReturn = $vData
	Return $vReturn
EndFunc    ;==>_SMTP_COMErrorHexNumber

Func _SMTP_COMErrorDescription($sData = Default)
	Local Static $sReturn = ''
	If $sData <> Default Then $sReturn = '### SMTP COM Error: ' & $sData
	Return $sReturn
EndFunc    ;==>_SMTP_COMErrorDescription

Func _SMTP_COMErrorScriptLine($iData = Default)
	Local Static $iReturn = ''
	If $iData <> Default Then $iReturn = $iData
	Return $iReturn
EndFunc    ;==>_SMTP_COMErrorScriptLine

Func __SMTP_COMErrorFunc($oSMTP_COMErrorObject)
	_SMTP_COMErrorHexNumber(Hex($oSMTP_COMErrorObject.number, 8))
	_SMTP_COMErrorDescription(StringStripWS($oSMTP_COMErrorObject.description, 3))
	_SMTP_COMErrorScriptLine($oSMTP_COMErrorObject.scriptline)
EndFunc    ;==>__SMTP_COMErrorFunc
#EndRegion  UDF Functions - COM Error Handler

#Region HELP DOC HINTs
#cs
	https://msdn.microsoft.com/en-us/library/ms526497(v=exchg.10).aspx
	http://support.microsoft.com/kb/286431
	http://support.microsoft.com/kb/313775
	http://support.microsoft.com/kb/302839

	DSNOptions Property
	https://msdn.microsoft.com/en-us/library/ms526559(v=exchg.10).aspx

	How To Send a Delivery Status Notification by Using CDO for Windows 2000
	https://support.microsoft.com/en-us/kb/302839

	SaveMessageToFile
	https://msdn.microsoft.com/en-us/library/aa488396(v=exchg.65).aspx

	https://www.hmailserver.com/forum/viewtopic.php?t=9039
	http://www.paulsadowski.com/wsh/cdo.htm
#ce
#EndRegion  HELP DOC HINTs
