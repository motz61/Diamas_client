import dbg
import app
import net
import ui
import ime
import snd
import wndMgr
import musicInfo
import serverInfo
import systemSetting
import ServerStateChecker
import localeInfo
import constInfo
import uiCommon
import time
import ime
import uiScriptLocale

VIRTUAL_KEYBOARD_NUM_KEYS = 46

app.SetGuildMarkPath("test")
class ConnectingDialog(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.__LoadDialog()
		self.eventTimeOver = lambda *arg: None
		self.eventExit = lambda *arg: None

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __LoadDialog(self):
		try:
			PythonScriptLoader = ui.PythonScriptLoader()
			PythonScriptLoader.LoadScriptFile(self, "UIScript/ConnectingDialog.py")

			self.board = self.GetChild("board")
			self.message = self.GetChild("message")
			self.countdownMessage = self.GetChild("countdown_message")

		except:
			import exception
			exception.Abort("ConnectingDialog.LoadDialog.BindObject")

	def Open(self, waitTime):
		curTime = time.clock()
		self.endTime = curTime + waitTime

		self.Lock()
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.Unlock()
		self.Hide()

	def Destroy(self):
		self.Hide()
		self.ClearDictionary()

	def SetText(self, text):
		self.message.SetText(text)

	def SetCountDownMessage(self, waitTime):
		self.countdownMessage.SetText("%.0f%s" % (waitTime, localeInfo.SECOND))

	def SAFE_SetTimeOverEvent(self, event):
		self.eventTimeOver = ui.__mem_func__(event)

	def SAFE_SetExitEvent(self, event):
		self.eventExit = ui.__mem_func__(event)

	def OnUpdate(self):
		lastTime = max(0, self.endTime - time.clock())
		if 0 == lastTime:
			self.Close()
			self.eventTimeOver()
		else:
			self.SetCountDownMessage(self.endTime - time.clock())

	def OnPressExitKey(self):
		#self.eventExit()
		return True

class LoginWindow(ui.ScriptWindow):
	def __init__(self, stream):
		print "NEW LOGIN WINDOW  ----------------------------------------------------------------------------"
		ui.ScriptWindow.__init__(self)
		net.SetPhaseWindow(net.PHASE_WINDOW_LOGIN, self)
		net.SetAccountConnectorHandler(self)

		self.matrixInputChanceCount = 0
		self.lastLoginTime = 0
		self.inputDialog = None
		self.connectingDialog = None
		self.stream=stream
		self.isNowCountDown=False
		self.isStartError=False

		self.xServerBoard = 0
		self.yServerBoard = 0

		self.loadingImage = None

		self.virtualKeyboard = None
		self.virtualKeyboardMode = "ALPHABET"
		self.virtualKeyboardIsUpper = False

		app.loggined = False
		# @fixme001 BEGIN (timeOutMsg and timeOutOk undefined)
		self.timeOutMsg = False
		self.timeOutOk = False
		# @fixme001 END

	def __del__(self):
		net.ClearPhaseWindow(net.PHASE_WINDOW_LOGIN, self)
		net.SetAccountConnectorHandler(0)
		ui.ScriptWindow.__del__(self)
		print "---------------------------------------------------------------------------- DELETE LOGIN WINDOW"

	def Open(self):
		ServerStateChecker.Create(self)

		print "LOGIN WINDOW OPEN ----------------------------------------------------------------------------"

		self.loginFailureMsgDict={
			#"DEFAULT" : localeInfo.LOGIN_FAILURE_UNKNOWN,

			"ALREADY"	: localeInfo.LOGIN_FAILURE_ALREAY,
			"NOID"		: localeInfo.LOGIN_FAILURE_NOT_EXIST_ID,
			"WRONGPWD"	: localeInfo.LOGIN_FAILURE_WRONG_PASSWORD,
			"FULL"		: localeInfo.LOGIN_FAILURE_TOO_MANY_USER,
			"SHUTDOWN"	: localeInfo.LOGIN_FAILURE_SHUTDOWN,
			"REPAIR"	: localeInfo.LOGIN_FAILURE_REPAIR_ID,
			"BLOCK"		: localeInfo.LOGIN_FAILURE_BLOCK_ID,
			"WRONGMAT"	: localeInfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER,
			"QUIT"		: localeInfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER_TRIPLE,
			"BESAMEKEY"	: localeInfo.LOGIN_FAILURE_BE_SAME_KEY,
			"NOTAVAIL"	: localeInfo.LOGIN_FAILURE_NOT_AVAIL,
			"NOBILL"	: localeInfo.LOGIN_FAILURE_NOBILL,
			"BLKLOGIN"	: localeInfo.LOGIN_FAILURE_BLOCK_LOGIN,
			"WEBBLK"	: localeInfo.LOGIN_FAILURE_WEB_BLOCK,
			"BADSCLID"	: localeInfo.LOGIN_FAILURE_WRONG_SOCIALID,
			"AGELIMIT"	: localeInfo.LOGIN_FAILURE_SHUTDOWN_TIME,
		}

		self.loginFailureFuncDict = {
			"WRONGPWD"	: self.__DisconnectAndInputPassword,
			"QUIT"		: app.Exit,
		}

		self.SetSize(wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())
		self.SetWindowName("LoginWindow")

		if not self.__LoadScript(uiScriptLocale.LOCALE_UISCRIPT_PATH + "LoginWindow.py"):
			dbg.TraceError("LoginWindow.Open - __LoadScript Error")
			return

		self.__LoadLoginInfo("loginInfo.xml")

		if app.loggined:
			self.loginFailureFuncDict = {
				"WRONGPWD"	: app.Exit,
				"WRONGMAT"	: app.Exit,
				"QUIT"		: app.Exit,
			}

		if musicInfo.loginMusic != "":
			snd.SetMusicVolume(systemSetting.GetMusicVolume())
			snd.FadeInMusic("BGM/"+musicInfo.loginMusic)

		snd.SetSoundVolume(systemSetting.GetSoundVolume())

		# pevent key "[" "]"
		ime.AddExceptKey(91)
		ime.AddExceptKey(93)

		self.Show()

		connectingIP = self.stream.GetConnectAddr()
		if connectingIP:
			self.__OpenLoginBoard()
		else:
			self.__RefreshServerList()
			self.__OpenServerBoard()

		app.ShowCursor()

	def Close(self):
		if self.connectingDialog:
			self.connectingDialog.Close()
		self.connectingDialog = None

		ServerStateChecker.Initialize(self)

		print "---------------------------------------------------------------------------- CLOSE LOGIN WINDOW "
		if musicInfo.loginMusic != "" and musicInfo.selectMusic != "":
			snd.FadeOutMusic("BGM/"+musicInfo.loginMusic)

		self.idEditLine.SetTabEvent(0)
		self.idEditLine.SetReturnEvent(0)
		self.pwdEditLine.SetReturnEvent(0)
		self.pwdEditLine.SetTabEvent(0)

		self.connectBoard = None
		self.loginBoard = None
		self.idEditLine = None
		self.pwdEditLine = None
		self.inputDialog = None
		self.connectingDialog = None
		self.loadingImage = None

		self.serverBoard				= None
		self.serverList					= None
		self.channelList				= None

		self.VIRTUAL_KEY_ALPHABET_LOWERS = None
		self.VIRTUAL_KEY_ALPHABET_UPPERS = None
		self.VIRTUAL_KEY_SYMBOLS = None
		self.VIRTUAL_KEY_NUMBERS = None

		# VIRTUAL_KEYBOARD_BUG_FIX
		if self.virtualKeyboard:
			for keyIndex in xrange(0, VIRTUAL_KEYBOARD_NUM_KEYS+1):
				key = self.GetChild2("key_%d" % keyIndex)
				if key:
					key.SetEvent(None)

			self.GetChild("key_space").SetEvent(None)
			self.GetChild("key_backspace").SetEvent(None)
			self.GetChild("key_enter").SetEvent(None)
			self.GetChild("key_shift").SetToggleDownEvent(None)
			self.GetChild("key_shift").SetToggleUpEvent(None)
			self.GetChild("key_at").SetToggleDownEvent(None)
			self.GetChild("key_at").SetToggleUpEvent(None)

			self.virtualKeyboard = None

		self.KillFocus()
		self.Hide()

		self.stream.popupWindow.Close()
		self.loginFailureFuncDict=None

		ime.ClearExceptKey()

		app.HideCursor()

	def __SaveChannelInfo(self):
		try:
			file=open("config/channel.cfg", "w")
			file.write("%d %d %d" % (self.__GetServerID(), self.__GetChannelID(), self.__GetRegionID()))
		except:
			print "LoginWindow.__SaveChannelInfo - SaveError"

	def __LoadChannelInfo(self):
		try:
			file=open("config/channel.cfg")
			lines=file.readlines()

			if len(lines)>0:
				tokens=lines[0].split()

				selServerID=int(tokens[0])
				selChannelID=int(tokens[1])

				if len(tokens) == 3:
					regionID = int(tokens[2])

				return regionID, selServerID, selChannelID

		except:
			print "LoginWindow.__LoadChannelInfo - OpenError"
			return -1, -1, -1

	def __ExitGame(self):
		app.Exit()

	def SetIDEditLineFocus(self):
		if self.idEditLine:
			self.idEditLine.SetFocus()

	def SetPasswordEditLineFocus(self):
		if constInfo.ENABLE_CLEAN_DATA_IF_FAIL_LOGIN:
			if self.idEditLine:
				self.idEditLine.SetText("")
				self.idEditLine.SetFocus()

			if self.pwdEditLine != None:
				self.pwdEditLine.SetText("")
		else:
			if self.pwdEditLine:
				self.pwdEditLine.SetFocus()


	def OnEndCountDown(self):
		self.isNowCountDown = False
		self.timeOutMsg = False

		self.OnConnectFailure()

	def OnConnectFailure(self):
		if self.isNowCountDown:
			return

		snd.PlaySound("sound/ui/loginfail.wav")

		if self.connectingDialog:
			self.connectingDialog.Close()
		self.connectingDialog = None

		if app.loggined:
			self.PopupNotifyMessage(localeInfo.LOGIN_CONNECT_FAILURE, self.__ExitGame)
		elif self.timeOutMsg:
			self.PopupNotifyMessage(localeInfo.LOGIN_FAILURE_TIMEOUT, self.SetPasswordEditLineFocus)
		else:
			self.PopupNotifyMessage(localeInfo.LOGIN_CONNECT_FAILURE, self.SetPasswordEditLineFocus)

	def OnHandShake(self):
		snd.PlaySound("sound/ui/loginok.wav")
		self.PopupDisplayMessage(localeInfo.LOGIN_CONNECT_SUCCESS)

	def OnLoginStart(self):
		self.PopupDisplayMessage(localeInfo.LOGIN_PROCESSING)

	def OnLoginFailure(self, error):
		if self.connectingDialog:
			self.connectingDialog.Close()
		self.connectingDialog = None

		try:
			loginFailureMsg = self.loginFailureMsgDict[error]
		except KeyError:
			loginFailureMsg = localeInfo.LOGIN_FAILURE_UNKNOWN  + error

		loginFailureFunc=self.loginFailureFuncDict.get(error, self.SetPasswordEditLineFocus)

		if app.loggined:
			self.PopupNotifyMessage(loginFailureMsg, self.__ExitGame)
		else:
			self.PopupNotifyMessage(loginFailureMsg, loginFailureFunc)

		snd.PlaySound("sound/ui/loginfail.wav")

	def __DisconnectAndInputID(self):
		if self.connectingDialog:
			self.connectingDialog.Close()
		self.connectingDialog = None

		self.SetIDEditLineFocus()
		net.Disconnect()

	def __DisconnectAndInputPassword(self):
		if self.connectingDialog:
			self.connectingDialog.Close()
		self.connectingDialog = None

		self.SetPasswordEditLineFocus()
		net.Disconnect()

	def __LoadScript(self, fileName):
		import dbg
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, fileName)
		except:
			import exception
			exception.Abort("LoginWindow.__LoadScript.LoadObject")
		try:
			GetObject=self.GetChild
			self.serverBoard			= GetObject("ServerBoard")
			self.serverList				= GetObject("ServerList")
			self.channelList			= GetObject("ChannelList")
			self.serverSelectButton		= GetObject("ServerSelectButton")
			self.serverExitButton		= GetObject("ServerExitButton")
			self.connectBoard			= GetObject("ConnectBoard")
			self.loginBoard				= GetObject("LoginBoard")
			self.idEditLine				= GetObject("ID_EditLine")
			self.pwdEditLine			= GetObject("Password_EditLine")
			self.serverInfo				= GetObject("ConnectName")
			self.selectConnectButton	= GetObject("SelectConnectButton")
			self.loginButton			= GetObject("LoginButton")
			self.loginExitButton		= GetObject("LoginExitButton")

			self.virtualKeyboard		= self.GetChild2("VirtualKeyboard")

			if self.virtualKeyboard:
				self.VIRTUAL_KEY_ALPHABET_UPPERS = localeInfo.VIRTUAL_KEY_ALPHABET_UPPERS
				self.VIRTUAL_KEY_ALPHABET_LOWERS = "".join([localeInfo.VIRTUAL_KEY_ALPHABET_LOWERS[localeInfo.VIRTUAL_KEY_ALPHABET_UPPERS.index(e)] for e in self.VIRTUAL_KEY_ALPHABET_UPPERS])
				self.VIRTUAL_KEY_SYMBOLS = localeInfo.VIRTUAL_KEY_SYMBOLS
				self.VIRTUAL_KEY_NUMBERS = localeInfo.VIRTUAL_KEY_NUMBERS
				self.__VirtualKeyboard_SetAlphabetMode()

				self.GetChild("key_space").SetEvent(lambda : self.__VirtualKeyboard_PressKey(' '))
				self.GetChild("key_backspace").SetEvent(lambda : self.__VirtualKeyboard_PressBackspace())
				self.GetChild("key_enter").SetEvent(lambda : self.__VirtualKeyboard_PressReturn())
				self.GetChild("key_shift").SetToggleDownEvent(lambda : self.__VirtualKeyboard_SetUpperMode())
				self.GetChild("key_shift").SetToggleUpEvent(lambda : self.__VirtualKeyboard_SetLowerMode())
				self.GetChild("key_at").SetToggleDownEvent(lambda : self.__VirtualKeyboard_SetSymbolMode())
				self.GetChild("key_at").SetToggleUpEvent(lambda : self.__VirtualKeyboard_SetAlphabetMode())

		except:
			import exception
			exception.Abort("LoginWindow.__LoadScript.BindObject")

		self.selectConnectButton.SetEvent(ui.__mem_func__(self.__OnClickSelectConnectButton))

		self.serverBoard.OnKeyUp = ui.__mem_func__(self.__ServerBoard_OnKeyUp)
		self.xServerBoard, self.yServerBoard = self.serverBoard.GetLocalPosition()

		self.serverSelectButton.SetEvent(ui.__mem_func__(self.__OnClickSelectServerButton))
		self.serverExitButton.SetEvent(ui.__mem_func__(self.__OnClickExitButton))

		self.loginButton.SetEvent(ui.__mem_func__(self.__OnClickLoginButton))
		self.loginExitButton.SetEvent(ui.__mem_func__(self.__OnClickExitButton))

		self.serverList.SetEvent(ui.__mem_func__(self.__OnSelectServer))

		self.idEditLine.SetReturnEvent(ui.__mem_func__(self.pwdEditLine.SetFocus))
		self.idEditLine.SetTabEvent(ui.__mem_func__(self.pwdEditLine.SetFocus))

		self.pwdEditLine.SetReturnEvent(ui.__mem_func__(self.__OnClickLoginButton))
		self.pwdEditLine.SetTabEvent(ui.__mem_func__(self.idEditLine.SetFocus))

		return 1

	def __VirtualKeyboard_SetKeys(self, keyCodes):
		uiDefFontBackup = localeInfo.UI_DEF_FONT
		localeInfo.UI_DEF_FONT = localeInfo.UI_DEF_FONT_LARGE

		keyIndex = 1
		for keyCode in keyCodes:
			key = self.GetChild2("key_%d" % keyIndex)
			if key:
				key.SetEvent(lambda x=keyCode: self.__VirtualKeyboard_PressKey(x))
				key.SetText(keyCode)
				key.ButtonText.SetFontColor(0, 0, 0)
				keyIndex += 1

		for keyIndex in xrange(keyIndex, VIRTUAL_KEYBOARD_NUM_KEYS+1):
			key = self.GetChild2("key_%d" % keyIndex)
			if key:
				key.SetEvent(lambda x=' ': self.__VirtualKeyboard_PressKey(x))
				key.SetText(' ')

		localeInfo.UI_DEF_FONT = uiDefFontBackup

	def __VirtualKeyboard_PressKey(self, code):
		ime.PasteString(code)

	def __VirtualKeyboard_PressBackspace(self):
		ime.PasteBackspace()

	def __VirtualKeyboard_PressReturn(self):
		ime.PasteReturn()

	def __VirtualKeyboard_SetUpperMode(self):
		self.virtualKeyboardIsUpper = True

		if self.virtualKeyboardMode == "ALPHABET":
			self.__VirtualKeyboard_SetKeys(self.VIRTUAL_KEY_ALPHABET_UPPERS)
		elif self.virtualKeyboardMode == "NUMBER":
			self.__VirtualKeyboard_SetKeys(self.VIRTUAL_KEY_SYMBOLS)
		else:
			self.__VirtualKeyboard_SetKeys(self.VIRTUAL_KEY_NUMBERS)

	def __VirtualKeyboard_SetLowerMode(self):
		self.virtualKeyboardIsUpper = False

		if self.virtualKeyboardMode == "ALPHABET":
			self.__VirtualKeyboard_SetKeys(self.VIRTUAL_KEY_ALPHABET_LOWERS)
		elif self.virtualKeyboardMode == "NUMBER":
			self.__VirtualKeyboard_SetKeys(self.VIRTUAL_KEY_NUMBERS)
		else:
			self.__VirtualKeyboard_SetKeys(self.VIRTUAL_KEY_SYMBOLS)

	def __VirtualKeyboard_SetAlphabetMode(self):
		self.virtualKeyboardIsUpper = False
		self.virtualKeyboardMode = "ALPHABET"
		self.__VirtualKeyboard_SetKeys(self.VIRTUAL_KEY_ALPHABET_LOWERS)

	def __VirtualKeyboard_SetNumberMode(self):
		self.virtualKeyboardIsUpper = False
		self.virtualKeyboardMode = "NUMBER"
		self.__VirtualKeyboard_SetKeys(self.VIRTUAL_KEY_NUMBERS)

	def __VirtualKeyboard_SetSymbolMode(self):
		self.virtualKeyboardIsUpper = False
		self.virtualKeyboardMode = "SYMBOL"
		self.__VirtualKeyboard_SetKeys(self.VIRTUAL_KEY_SYMBOLS)

	def Connect(self, id, pwd):
		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(localeInfo.LOGIN_CONNETING, self.SetPasswordEditLineFocus, localeInfo.UI_CANCEL)

		self.stream.SetLoginInfo(id, pwd)
		self.stream.Connect()

	def __OnClickExitButton(self):
		self.stream.SetPhaseWindow(0)

	def __SetServerInfo(self, name):
		net.SetServerInfo(name.strip())
		self.serverInfo.SetText(name)

	def __LoadLoginInfo(self, loginInfoFileName):
		if not app.IsExistFile(loginInfoFileName):
			return
			
		def getValue(element, name, default):
			if [] != element.getElementsByTagName(name):
				return element.getElementsByTagName(name).item(0).firstChild.nodeValue
			else:
				return default

		self.id = None
		self.pwd = None
		self.loginnedServer = None
		self.loginnedChannel = None
		app.loggined = False

		self.loginInfo = True

		from xml.dom.minidom import parse
		try:
			f = open(loginInfoFileName, "r")
			dom = parse(f)
		except:
			return
		serverLst = dom.getElementsByTagName("server")
		if [] != dom.getElementsByTagName("logininfo"):
			logininfo = dom.getElementsByTagName("logininfo")[0]
		else:
			return

		try:
			server_name = logininfo.getAttribute("name")
			channel_idx = int(logininfo.getAttribute("channel_idx"))
		except:
			return

		try:
			matched = False

			for k, v in serverInfo.REGION_DICT[0].iteritems():
				if v["name"] == server_name:
					account_addr = serverInfo.REGION_AUTH_SERVER_DICT[0][k]["ip"]
					account_port = serverInfo.REGION_AUTH_SERVER_DICT[0][k]["port"]

					channel_info = v["channel"][channel_idx]
					channel_name = channel_info["name"]
					addr = channel_info["ip"]
					port = channel_info["tcp_port"]

					net.SetMarkServer(addr, port)
					self.stream.SetConnectInfo(addr, port, account_addr, account_port)

					matched = True
					break

			if False == matched:
				return
		except:
			return

		self.__SetServerInfo("%s, %s " % (server_name, channel_name))
		id = getValue(logininfo, "id", "")
		pwd = getValue(logininfo, "pwd", "")
		self.idEditLine.SetText(id)
		self.pwdEditLine.SetText(pwd)
		slot = getValue(logininfo, "slot", "0")
		locale = getValue(logininfo, "locale", "")
		locale_dir = getValue(logininfo, "locale_dir", "")
		is_auto_login = int(getValue(logininfo, "auto_login", "0"))

		self.stream.SetCharacterSlot(int(slot))
		self.stream.isAutoLogin=is_auto_login
		self.stream.isAutoSelect=is_auto_login

		if locale and locale_dir:
			app.ForceSetLocale(locale, locale_dir)

		if 0 != is_auto_login:
			self.Connect(id, pwd)

		return


	def PopupDisplayMessage(self, msg):
		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg)

	def PopupNotifyMessage(self, msg, func=0):
		if not func:
			func=self.EmptyFunc

		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg, func, localeInfo.UI_OK)

	def __OnCloseInputDialog(self):
		if self.inputDialog:
			self.inputDialog.Close()
		self.inputDialog = None
		return True

	def OnPressExitKey(self):
		self.stream.popupWindow.Close()
		self.stream.SetPhaseWindow(0)
		return True

	def OnExit(self):
		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(localeInfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER_TRIPLE, app.Exit, localeInfo.UI_OK)

	def OnUpdate(self):
		ServerStateChecker.Update()

	def EmptyFunc(self):
		pass

	#####################################################################################

	def __ServerBoard_OnKeyUp(self, key):
		if self.serverBoard.IsShow():
			if app.DIK_RETURN==key:
				self.__OnClickSelectServerButton()
		return True

	def __GetRegionID(self):
		return 0

	def __GetServerID(self):
		return self.serverList.GetSelectedItem()

	def __GetChannelID(self):
		return self.channelList.GetSelectedItem()

	def __ServerIDToServerIndex(self, regionID, targetServerID):
		try:
			regionDict = serverInfo.REGION_DICT[regionID]
		except KeyError:
			return -1

		retServerIndex = 0
		for eachServerID, regionDataDict in regionDict.items():
			if eachServerID == targetServerID:
				return retServerIndex

			retServerIndex += 1

		return -1

	def __ChannelIDToChannelIndex(self, channelID):
		return channelID - 1

	def __OpenServerBoard(self):
		loadRegionID, loadServerID, loadChannelID = self.__LoadChannelInfo()

		serverIndex = self.__ServerIDToServerIndex(loadRegionID, loadServerID)
		channelIndex = self.__ChannelIDToChannelIndex(loadChannelID)

		self.serverList.SelectItem(serverIndex)

		if constInfo.ENABLE_RANDOM_CHANNEL_SEL:
			self.channelList.SelectItem(app.GetRandom(0, self.channelList.GetItemCount()))
		else:
			if channelIndex >= 0:
				self.channelList.SelectItem(channelIndex)


		self.serverBoard.SetPosition(self.xServerBoard, self.yServerBoard)
		self.serverBoard.Show()
		self.connectBoard.Hide()
		self.loginBoard.Hide()

		if self.virtualKeyboard:
			self.virtualKeyboard.Hide()

		if app.loggined:
			self.serverList.SelectItem(self.loginnedServer-1)
			self.channelList.SelectItem(self.loginnedChannel-1)
			self.__OnClickSelectServerButton()

	def __OpenLoginBoard(self):
		self.serverExitButton.SetEvent(ui.__mem_func__(self.__OnClickExitServerButton))
		self.serverExitButton.SetText(localeInfo.UI_CLOSE)

		self.serverBoard.SetPosition(self.xServerBoard, wndMgr.GetScreenHeight())
		self.serverBoard.Hide()

		if self.virtualKeyboard:
			self.virtualKeyboard.Show()

		if app.loggined:
			self.Connect(self.id, self.pwd)
			self.connectBoard.Hide()
			self.loginBoard.Hide()
		elif not self.stream.isAutoLogin:
			self.connectBoard.Show()
			self.loginBoard.Show()

		if not self.idEditLine:
			self.idEditLine.SetText("")
		if not self.pwdEditLine:
			self.pwdEditLine.SetText("")

		self.idEditLine.SetFocus()

	def __OnSelectRegionGroup(self):
		self.__RefreshServerList()

	def __OnSelectSettlementArea(self):
		regionID = self.__GetRegionID()
		serverID = self.serverListOnRegionBoard.GetSelectedItem()

		serverIndex = self.__ServerIDToServerIndex(regionID, serverID)
		self.serverList.SelectItem(serverIndex)

		self.__OnSelectServer()

	def __RefreshServerList(self):
		regionID = self.__GetRegionID()

		if not serverInfo.REGION_DICT.has_key(regionID):
			return

		self.serverList.ClearItem()

		regionDict = serverInfo.REGION_DICT[regionID]

		visible_index = 1
		for id, regionDataDict in regionDict.items():
			name = regionDataDict.get("name", "noname")

			try:
				server_id = serverInfo.SERVER_ID_DICT[id]
			except:
				server_id = visible_index

			self.serverList.InsertItem(id, "  %02d. %s" % (int(server_id), name))

			visible_index += 1

	def __OnSelectServer(self):
		self.__OnCloseInputDialog()
		self.__RequestServerStateList()
		self.__RefreshServerStateList()

	def __RequestServerStateList(self):
		regionID = self.__GetRegionID()
		serverID = self.__GetServerID()

		try:
			channelDict = serverInfo.REGION_DICT[regionID][serverID]["channel"]
		except:
			print " __RequestServerStateList - serverInfo.REGION_DICT(%d, %d)" % (regionID, serverID)
			return

		ServerStateChecker.Initialize();
		for id, channelDataDict in channelDict.items():
			key=channelDataDict["key"]
			ip=channelDataDict["ip"]
			port=channelDataDict["tcp_port"]
			ServerStateChecker.AddChannel(key, ip, port)

		ServerStateChecker.Request()

	def __RefreshServerStateList(self):

		regionID = self.__GetRegionID()
		serverID = self.__GetServerID()
		bakChannelID = self.channelList.GetSelectedItem()

		self.channelList.ClearItem()

		try:
			channelDict = serverInfo.REGION_DICT[regionID][serverID]["channel"]
		except:
			print " __RequestServerStateList - serverInfo.REGION_DICT(%d, %d)" % (regionID, serverID)
			return

		for channelID, channelDataDict in channelDict.items():
			channelName = channelDataDict["name"]
			channelState = channelDataDict["state"]
			self.channelList.InsertItem(channelID, " %s %s" % (channelName, channelState))

		self.channelList.SelectItem(bakChannelID-1)

	def __GetChannelName(self, regionID, selServerID, selChannelID):
		try:
			return serverInfo.REGION_DICT[regionID][selServerID]["channel"][selChannelID]["name"]
		except KeyError:
			if 9==selChannelID:
				return localeInfo.CHANNEL_PVP
			else:
				return localeInfo.CHANNEL_NORMAL % (selChannelID)

	def NotifyChannelState(self, addrKey, state):
		try:
			stateName=serverInfo.STATE_DICT[state]
		except:
			stateName=serverInfo.STATE_NONE

		regionID=int(addrKey/1000)
		serverID=int(addrKey/10) % 100
		channelID=addrKey%10

		try:
			serverInfo.REGION_DICT[regionID][serverID]["channel"][channelID]["state"] = stateName
			self.__RefreshServerStateList()

		except:
			import exception
			exception.Abort(localeInfo.CHANNEL_NOT_FIND_INFO)

	def __OnClickExitServerButton(self):
		print "exit server"
		self.__OpenLoginBoard()

	def __OnClickSelectRegionButton(self):
		regionID = self.__GetRegionID()
		serverID = self.__GetServerID()

		if (not serverInfo.REGION_DICT.has_key(regionID)):
			self.PopupNotifyMessage(localeInfo.CHANNEL_SELECT_REGION)
			return

		if (not serverInfo.REGION_DICT[regionID].has_key(serverID)):
			self.PopupNotifyMessage(localeInfo.CHANNEL_SELECT_SERVER)
			return

		self.__SaveChannelInfo()

		self.serverExitButton.SetEvent(ui.__mem_func__(self.__OnClickExitServerButton))
		self.serverExitButton.SetText(localeInfo.UI_CLOSE)

		self.__RefreshServerList()
		self.__OpenServerBoard()

	def __OnClickSelectServerButton(self):
		regionID = self.__GetRegionID()
		serverID = self.__GetServerID()
		channelID = self.__GetChannelID()

		if (not serverInfo.REGION_DICT.has_key(regionID)):
			self.PopupNotifyMessage(localeInfo.CHANNEL_SELECT_REGION)
			return

		if (not serverInfo.REGION_DICT[regionID].has_key(serverID)):
			self.PopupNotifyMessage(localeInfo.CHANNEL_SELECT_SERVER)
			return

		try:
			channelDict = serverInfo.REGION_DICT[regionID][serverID]["channel"]
		except KeyError:
			return

		try:
			state = channelDict[channelID]["state"]
		except KeyError:
			self.PopupNotifyMessage(localeInfo.CHANNEL_SELECT_CHANNEL)
			return

		if state == serverInfo.STATE_DICT[3]:
			self.PopupNotifyMessage(localeInfo.CHANNEL_NOTIFY_FULL)
			return

		self.__SaveChannelInfo()

		try:
			serverName = serverInfo.REGION_DICT[regionID][serverID]["name"]
			channelName = serverInfo.REGION_DICT[regionID][serverID]["channel"][channelID]["name"]
			addrKey = serverInfo.REGION_DICT[regionID][serverID]["channel"][channelID]["key"]
		except:
			print " ERROR __OnClickSelectServerButton(%d, %d, %d)" % (regionID, serverID, channelID)
			serverName = localeInfo.CHANNEL_EMPTY_SERVER
			channelName = localeInfo.CHANNEL_NORMAL % channelID

		self.__SetServerInfo("%s, %s " % (serverName, channelName))

		try:
			ip = serverInfo.REGION_DICT[regionID][serverID]["channel"][channelID]["ip"]
			tcp_port = serverInfo.REGION_DICT[regionID][serverID]["channel"][channelID]["tcp_port"]
		except:
			import exception
			exception.Abort("LoginWindow.__OnClickSelectServerButton - ???????? ???????? ????????")

		try:
			account_ip = serverInfo.REGION_AUTH_SERVER_DICT[regionID][serverID]["ip"]
			account_port = serverInfo.REGION_AUTH_SERVER_DICT[regionID][serverID]["port"]
		except:
			account_ip = 0
			account_port = 0

		try:
			markKey = regionID*1000 + serverID*10
			markAddrValue=serverInfo.MARKADDR_DICT[markKey]
			net.SetMarkServer(markAddrValue["ip"], markAddrValue["tcp_port"])
			app.SetGuildMarkPath(markAddrValue["mark"])
			app.SetGuildSymbolPath(markAddrValue["symbol_path"])
		except:
			import exception
			exception.Abort("LoginWindow.__OnClickSelectServerButton - ???????? ???????? ????????")

		self.stream.SetConnectInfo(ip, tcp_port, account_ip, account_port)
		self.__OpenLoginBoard()

	def __OnClickSelectConnectButton(self):
		self.__RefreshServerList()
		self.__OpenServerBoard()

	def __OnClickLoginButton(self):
		id = self.idEditLine.GetText()
		pwd = self.pwdEditLine.GetText()

		if not id:
			self.PopupNotifyMessage(localeInfo.LOGIN_INPUT_ID, self.SetIDEditLineFocus)
			return

		if not pwd:
			self.PopupNotifyMessage(localeInfo.LOGIN_INPUT_PASSWORD, self.SetPasswordEditLineFocus)
			return

		self.Connect(id, pwd)
