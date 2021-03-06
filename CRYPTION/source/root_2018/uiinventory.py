import ui
import playerm2g2
import mouseModule
import m2netm2g
import app
import snd
import item
import playerm2g2
import chatm2g
import grp
import uiScriptLocale
import uiRefine
import uiAttachMetin
import uiPickMoney
import uiCommon
import uiPrivateShopBuilder # 개인상점 열동안 ItemMove 방지
import localeInfo
import constInfo
import ime
import wndMgr

if app.ENABLE_GROWTH_PET_SYSTEM:
	import uiPetInfo

if app.ENABLE_CHEQUE_SYSTEM:
	import uiToolTip
	import uiPickETC
		
ITEM_MALL_BUTTON_ENABLE = True
ITEM_FLAG_APPLICABLE = 1 << 14

class CostumeWindow(ui.ScriptWindow):

	def __init__(self, wndInventory):
		import exception
		
		if not wndInventory:
			exception.Abort("wndInventory parameter must be set to InventoryWindow")
			return						
			 	 
		ui.ScriptWindow.__init__(self)

		self.isLoaded = 0
		self.wndInventory = wndInventory;

		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Show(self):
		self.__LoadWindow()
		self.RefreshCostumeSlot()

		ui.ScriptWindow.Show(self)

	def Close(self):
		self.Hide()

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/CostumeWindow.py")
		except:
			import exception
			exception.Abort("CostumeWindow.LoadWindow.LoadObject")

		try:
			wndEquip = self.GetChild("CostumeSlot")
			self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))
			
		except:
			import exception
			exception.Abort("CostumeWindow.LoadWindow.BindObject")

		## Equipment
		wndEquip.SetOverInItemEvent(ui.__mem_func__(self.wndInventory.OverInItem))
		wndEquip.SetOverOutItemEvent(ui.__mem_func__(self.wndInventory.OverOutItem))
		wndEquip.SetUnselectItemSlotEvent(ui.__mem_func__(self.wndInventory.UseItemSlot))
		wndEquip.SetUseSlotEvent(ui.__mem_func__(self.wndInventory.UseItemSlot))						
		wndEquip.SetSelectEmptySlotEvent(ui.__mem_func__(self.wndInventory.SelectEmptySlot))
		wndEquip.SetSelectItemSlotEvent(ui.__mem_func__(self.wndInventory.SelectItemSlot))

		self.wndEquip = wndEquip

	def RefreshCostumeSlot(self):
		getItemVNum=playerm2g2.GetItemIndex
		
		for i in xrange(item.COSTUME_SLOT_COUNT):
			slotNumber = item.COSTUME_SLOT_START + i
			self.wndEquip.SetItemSlot(slotNumber, getItemVNum(slotNumber), 0)

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if not playerm2g2.GetChangeLookVnum(playerm2g2.EQUIPMENT, slotNumber) == 0:
					self.wndEquip.SetSlotCoverImage(slotNumber,"icon/item/ingame_convert_Mark.tga")
				else:
					self.wndEquip.EnableSlotCoverImage(slotNumber,False)

		if app.ENABLE_WEAPON_COSTUME_SYSTEM:
			self.wndEquip.SetItemSlot(item.COSTUME_SLOT_WEAPON, getItemVNum(item.COSTUME_SLOT_WEAPON), 0)

			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if not playerm2g2.GetChangeLookVnum(playerm2g2.EQUIPMENT, item.COSTUME_SLOT_WEAPON) == 0:
					self.wndEquip.SetSlotCoverImage(item.COSTUME_SLOT_WEAPON,"icon/item/ingame_convert_Mark.tga")
				else:
					self.wndEquip.EnableSlotCoverImage(item.COSTUME_SLOT_WEAPON,False)

		self.wndEquip.RefreshSlot()
		
class BeltInventoryWindow(ui.ScriptWindow):

	def __init__(self, wndInventory):
		import exception

		if not wndInventory:
			exception.Abort("wndInventory parameter must be set to InventoryWindow")
			return						
			 	 
		ui.ScriptWindow.__init__(self)

		self.isLoaded = 0
		self.wndInventory = wndInventory;
		
		self.wndBeltInventoryLayer = None
		self.wndBeltInventorySlot = None
		self.expandBtn = None
		self.minBtn = None

		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Show(self, openBeltSlot = FALSE):
		self.__LoadWindow()
		self.RefreshSlot()

		ui.ScriptWindow.Show(self)
		
		if openBeltSlot:
			self.OpenInventory()
		else:
			self.CloseInventory()

	def Close(self):
		self.Hide()

	def IsOpeningInventory(self):
		return self.wndBeltInventoryLayer.IsShow()
		
	def OpenInventory(self):
		self.wndBeltInventoryLayer.Show()
		self.expandBtn.Hide()

		if localeInfo.IsARABIC() == 0:
			self.AdjustPositionAndSize()
				
	def CloseInventory(self):
		self.wndBeltInventoryLayer.Hide()
		self.expandBtn.Show()
		
		if localeInfo.IsARABIC() == 0:
			self.AdjustPositionAndSize()

	## 현재 인벤토리 위치를 기준으로 BASE 위치를 계산, 리턴.. 숫자 하드코딩하기 정말 싫지만 방법이 없다..
	def GetBasePosition(self):
		x, y = self.wndInventory.GetGlobalPosition()
		return x - 148, y + 241
		
	def AdjustPositionAndSize(self):
		bx, by = self.GetBasePosition()
		
		if self.IsOpeningInventory():			
			self.SetPosition(bx, by)
			self.SetSize(self.ORIGINAL_WIDTH, self.GetHeight())
			
		else:
			self.SetPosition(bx + 138, by);
			self.SetSize(10, self.GetHeight())

	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/BeltInventoryWindow.py")
		except:
			import exception
			exception.Abort("CostumeWindow.LoadWindow.LoadObject")

		try:
			self.ORIGINAL_WIDTH = self.GetWidth()
			wndBeltInventorySlot = self.GetChild("BeltInventorySlot")
			self.wndBeltInventoryLayer = self.GetChild("BeltInventoryLayer")
			self.expandBtn = self.GetChild("ExpandBtn")
			self.minBtn = self.GetChild("MinimizeBtn")
			
			self.expandBtn.SetEvent(ui.__mem_func__(self.OpenInventory))
			self.minBtn.SetEvent(ui.__mem_func__(self.CloseInventory))
			
			if localeInfo.IsARABIC() :
				self.expandBtn.SetPosition(self.expandBtn.GetWidth() - 2, 15)
				self.wndBeltInventoryLayer.SetPosition(self.wndBeltInventoryLayer.GetWidth() - 5, 0)
				self.minBtn.SetPosition(self.minBtn.GetWidth() + 3, 15)			
	
			for i in xrange(item.BELT_INVENTORY_SLOT_COUNT):
				slotNumber = item.BELT_INVENTORY_SLOT_START + i							
				wndBeltInventorySlot.SetCoverButton(slotNumber,	"d:/ymir work/ui/game/quest/slot_button_01.sub",\
												"d:/ymir work/ui/game/quest/slot_button_01.sub",\
												"d:/ymir work/ui/game/quest/slot_button_01.sub",\
												"d:/ymir work/ui/game/belt_inventory/slot_disabled.tga", FALSE, FALSE)									
			
		except:
			import exception
			exception.Abort("CostumeWindow.LoadWindow.BindObject")

		## Equipment
		wndBeltInventorySlot.SetOverInItemEvent(ui.__mem_func__(self.wndInventory.OverInItem))
		wndBeltInventorySlot.SetOverOutItemEvent(ui.__mem_func__(self.wndInventory.OverOutItem))
		wndBeltInventorySlot.SetUnselectItemSlotEvent(ui.__mem_func__(self.wndInventory.UseItemSlot))
		wndBeltInventorySlot.SetUseSlotEvent(ui.__mem_func__(self.wndInventory.UseItemSlot))						
		wndBeltInventorySlot.SetSelectEmptySlotEvent(ui.__mem_func__(self.wndInventory.SelectEmptySlot))
		wndBeltInventorySlot.SetSelectItemSlotEvent(ui.__mem_func__(self.wndInventory.SelectItemSlot))

		self.wndBeltInventorySlot = wndBeltInventorySlot

	def RefreshSlot(self):
		getItemVNum=playerm2g2.GetItemIndex
		
		for i in xrange(item.BELT_INVENTORY_SLOT_COUNT):
			slotNumber = item.BELT_INVENTORY_SLOT_START + i
			self.wndBeltInventorySlot.SetItemSlot(slotNumber, getItemVNum(slotNumber), playerm2g2.GetItemCount(slotNumber))
			self.wndBeltInventorySlot.SetAlwaysRenderCoverButton(slotNumber, TRUE)
			
			avail = "0"
			
			if playerm2g2.IsAvailableBeltInventoryCell(slotNumber):
				self.wndBeltInventorySlot.EnableCoverButton(slotNumber)				
			else:
				self.wndBeltInventorySlot.DisableCoverButton(slotNumber)				

		self.wndBeltInventorySlot.RefreshSlot()

		
class InventoryWindow(ui.ScriptWindow):

	if app.ENABLE_CHANGED_ATTR :
		USE_TYPE_TUPLE = ("USE_CLEAN_SOCKET", "USE_CHANGE_ATTRIBUTE", "USE_ADD_ATTRIBUTE", "USE_ADD_ATTRIBUTE2", "USE_ADD_ACCESSORY_SOCKET", "USE_PUT_INTO_ACCESSORY_SOCKET", "USE_PUT_INTO_BELT_SOCKET", "USE_PUT_INTO_RING_SOCKET", "USE_CHANGE_COSTUME_ATTR", "USE_RESET_COSTUME_ATTR", "USE_SELECT_ATTRIBUTE")
	else :
		USE_TYPE_TUPLE = ("USE_CLEAN_SOCKET", "USE_CHANGE_ATTRIBUTE", "USE_ADD_ATTRIBUTE", "USE_ADD_ATTRIBUTE2", "USE_ADD_ACCESSORY_SOCKET", "USE_PUT_INTO_ACCESSORY_SOCKET", "USE_PUT_INTO_BELT_SOCKET", "USE_PUT_INTO_RING_SOCKET", "USE_CHANGE_COSTUME_ATTR", "USE_RESET_COSTUME_ATTR")

	questionDialog = None
	tooltipItem = None
	wndCostume = None
	wndBelt = None
	dlgPickMoney = None
	if app.ENABLE_CHEQUE_SYSTEM:
		dlgPickETC = None
		
	sellingSlotNumber = -1
	isLoaded = 0
	isOpenedCostumeWindowWhenClosingInventory = 0		# 인벤토리 닫을 때 코스츔이 열려있었는지 여부-_-; 네이밍 ㅈㅅ
	isOpenedBeltWindowWhenClosingInventory = 0		# 인벤토리 닫을 때 벨트 인벤토리가 열려있었는지 여부-_-; 네이밍 ㅈㅅ

	interface = None
	
	if app.ENABLE_GROWTH_PET_SYSTEM:
		petHatchingWindow	= None
		petFeedWindow		= None
		petNameChangeWindow = None

	def __init__(self):
		ui.ScriptWindow.__init__(self)

		self.isOpenedBeltWindowWhenClosingInventory = 0		# 인벤토리 닫을 때 벨트 인벤토리가 열려있었는지 여부-_-; 네이밍 ㅈㅅ

		self.__LoadWindow()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Show(self):
		self.__LoadWindow()

		ui.ScriptWindow.Show(self)
		
		self.RefreshItemSlot()
		self.RefreshStatus()

		# 인벤토리를 닫을 때 코스츔이 열려있었다면 인벤토리를 열 때 코스츔도 같이 열도록 함.
		if self.isOpenedCostumeWindowWhenClosingInventory and self.wndCostume:
			self.wndCostume.Show() 

		# 인벤토리를 닫을 때 벨트 인벤토리가 열려있었다면 같이 열도록 함.
		if self.wndBelt:
			self.wndBelt.Show(self.isOpenedBeltWindowWhenClosingInventory)

	def BindInterfaceClass(self, interface):
		from _weakref import proxy
		self.interface = proxy(interface)
		
	def __LoadWindow(self):
		if self.isLoaded == 1:
			return

		self.isLoaded = 1

		try:
			pyScrLoader = ui.PythonScriptLoader()

			if ITEM_MALL_BUTTON_ENABLE:
				pyScrLoader.LoadScriptFile(self, uiScriptLocale.LOCALE_UISCRIPT_PATH + "InventoryWindow.py")
			else:
				pyScrLoader.LoadScriptFile(self, "UIScript/InventoryWindow.py")
		except:
			import exception
			exception.Abort("InventoryWindow.LoadWindow.LoadObject")

		try:
			wndItem = self.GetChild("ItemSlot")
			wndEquip = self.GetChild("EquipmentSlot")
			self.GetChild("TitleBar").SetCloseEvent(ui.__mem_func__(self.Close))
			self.wndMoney = self.GetChild("Money")
			self.wndMoneySlot = self.GetChild("Money_Slot")
			self.mallButton = self.GetChild2("MallButton")
			self.DSSButton = self.GetChild2("DSSButton")
			self.costumeButton = self.GetChild2("CostumeButton")

			if app.ENABLE_CHEQUE_SYSTEM:
				self.wndCheque = self.GetChild("Cheque")
				self.wndChequeSlot = self.GetChild("Cheque_Slot")
				
				self.wndMoneyIcon = self.GetChild("Money_Icon")
				self.wndChequeIcon = self.GetChild("Cheque_Icon")
				
				self.wndMoneyIcon.SetEvent(ui.__mem_func__(self.EventProgress), "mouse_over_in", 0)
				self.wndChequeIcon.SetEvent(ui.__mem_func__(self.EventProgress), "mouse_over_in", 1)
				
				self.wndMoneyIcon.SetEvent(ui.__mem_func__(self.EventProgress), "mouse_over_out", 0)
				self.wndChequeIcon.SetEvent(ui.__mem_func__(self.EventProgress), "mouse_over_out", 1)
				
				self.toolTip = uiToolTip.ToolTip()
				self.toolTip.ClearToolTip()
						
			self.inventoryTab = []
			self.inventoryTab.append(self.GetChild("Inventory_Tab_01"))
			self.inventoryTab.append(self.GetChild("Inventory_Tab_02"))

			self.equipmentTab = []
			self.equipmentTab.append(self.GetChild("Equipment_Tab_01"))
			self.equipmentTab.append(self.GetChild("Equipment_Tab_02"))

			# Belt Inventory Window
			self.wndBelt = None
			
			self.dlgQuestion = uiCommon.QuestionDialog2()
			self.dlgQuestion.Close()
		
			self.wndBelt = BeltInventoryWindow(self)

			self.listHighlightedAcceSlot = []
			
			if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
				self.listHighlightedSlot = []
				
			if app.ENABLE_GROWTH_PET_SYSTEM:
				self.PetItemQuestionDlg = uiCommon.QuestionDialog()
				self.PetItemQuestionDlg.Close()
			
		except:
			import exception
			exception.Abort("InventoryWindow.LoadWindow.BindObject")

		## Item
		wndItem.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
		wndItem.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
		wndItem.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndItem.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		wndItem.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

		## Equipment
		wndEquip.SetSelectEmptySlotEvent(ui.__mem_func__(self.SelectEmptySlot))
		wndEquip.SetSelectItemSlotEvent(ui.__mem_func__(self.SelectItemSlot))
		wndEquip.SetUnselectItemSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndEquip.SetUseSlotEvent(ui.__mem_func__(self.UseItemSlot))
		wndEquip.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		wndEquip.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))

		## PickMoneyDialog
		dlgPickMoney = uiPickMoney.PickMoneyDialog()
		dlgPickMoney.LoadDialog()
		dlgPickMoney.Hide()

		## PickETCDialog
		if app.ENABLE_CHEQUE_SYSTEM:
			dlgPickETC = uiPickETC.PickETCDialog()
			dlgPickETC.LoadDialog()
			dlgPickETC.Hide()
			self.dlgPickETC = dlgPickETC
		
		## RefineDialog
		self.refineDialog = uiRefine.RefineDialog()
		self.refineDialog.Hide()

		## AttachMetinDialog
		self.attachMetinDialog = uiAttachMetin.AttachMetinDialog()
		self.attachMetinDialog.Hide()

		## MoneySlot
		if app.ENABLE_CHEQUE_SYSTEM:
			self.wndMoneySlot.SetEvent(ui.__mem_func__(self.OpenPickMoneyDialog), 0)
			self.wndChequeSlot.SetEvent(ui.__mem_func__(self.OpenPickMoneyDialog), 1)
		else:
			self.wndMoneySlot.SetEvent(ui.__mem_func__(self.OpenPickMoneyDialog))

		self.inventoryTab[0].SetEvent(lambda arg=0: self.SetInventoryPage(arg))
		self.inventoryTab[1].SetEvent(lambda arg=1: self.SetInventoryPage(arg))
		self.inventoryTab[0].Down()

		self.equipmentTab[0].SetEvent(lambda arg=0: self.SetEquipmentPage(arg))
		self.equipmentTab[1].SetEvent(lambda arg=1: self.SetEquipmentPage(arg))
		self.equipmentTab[0].Down()
		self.equipmentTab[0].Hide()
		self.equipmentTab[1].Hide()

		self.wndItem = wndItem
		self.wndEquip = wndEquip
		self.dlgPickMoney = dlgPickMoney

		# MallButton
		if self.mallButton:
			self.mallButton.SetEvent(ui.__mem_func__(self.ClickMallButton))

		if self.DSSButton:
			self.DSSButton.SetEvent(ui.__mem_func__(self.ClickDSSButton)) 
		
		# Costume Button
		if self.costumeButton:
			self.costumeButton.SetEvent(ui.__mem_func__(self.ClickCostumeButton))

		self.wndCostume = None
		
 		#####

		## Refresh
		self.SetInventoryPage(0)
		self.SetEquipmentPage(0)
		self.RefreshItemSlot()
		self.RefreshStatus()

	def Destroy(self):
		self.ClearDictionary()

		self.dlgPickMoney.Destroy()
		self.dlgPickMoney = 0
		
		if app.ENABLE_CHEQUE_SYSTEM:
			self.dlgPickETC.Destroy()
			self.dlgPickETC = 0	

		self.refineDialog.Destroy()
		self.refineDialog = 0

		self.attachMetinDialog.Destroy()
		self.attachMetinDialog = 0

		self.tooltipItem = None
		self.wndItem = 0
		self.wndEquip = 0
		self.dlgPickMoney = 0
		self.wndMoney = 0
		self.wndMoneySlot = 0
		self.questionDialog = None
		self.mallButton = None
		self.DSSButton = None
		self.interface = None

		if app.ENABLE_CHEQUE_SYSTEM:
			self.wndCheque = 0
			self.wndChequeSlot = 0
			self.dlgPickETC = 0
		
		if self.wndCostume:
			self.wndCostume.Destroy()
			self.wndCostume = 0
			
		if self.wndBelt:
			self.wndBelt.Destroy()
			self.wndBelt = None
			
		self.inventoryTab = []
		self.equipmentTab = []
		
		if app.ENABLE_GROWTH_PET_SYSTEM:
			if self.petHatchingWindow:
				self.petHatchingWindow = None
				
			if self.petFeedWindow:
				self.petFeedWindow = None
				
			if self.petNameChangeWindow:
				self.petNameChangeWindow = None

	def Hide(self):
		if constInfo.GET_ITEM_QUESTION_DIALOG_STATUS():
			self.OnCloseQuestionDialog()
			return
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()

		if self.wndCostume:
			self.isOpenedCostumeWindowWhenClosingInventory = self.wndCostume.IsShow()			# 인벤토리 창이 닫힐 때 코스츔이 열려 있었는가?
			self.wndCostume.Close()
 
		if self.wndBelt:
			self.isOpenedBeltWindowWhenClosingInventory = self.wndBelt.IsOpeningInventory()		# 인벤토리 창이 닫힐 때 벨트 인벤토리도 열려 있었는가?
			print "Is Opening Belt Inven?? ", self.isOpenedBeltWindowWhenClosingInventory
			self.wndBelt.Close()
  
		if self.dlgPickMoney:
			self.dlgPickMoney.Close()
			
		if app.ENABLE_CHEQUE_SYSTEM:
			if self.dlgPickETC:
				self.dlgPickETC.Close()
		
		wndMgr.Hide(self.hWnd)
		
	
	def Close(self):
		self.Hide()

	def SetInventoryPage(self, page):
		self.inventoryPageIndex = page
		self.inventoryTab[1-page].SetUp()
		self.RefreshBagSlotWindow()

	def SetEquipmentPage(self, page):
		self.equipmentPageIndex = page
		self.equipmentTab[1-page].SetUp()
		self.RefreshEquipSlotWindow()

	def ClickMallButton(self):
		m2netm2g.SendChatPacket("/click_mall")

	# DSSButton
	def ClickDSSButton(self):
		self.interface.ToggleDragonSoulWindow()

	def ClickCostumeButton(self):
		if self.wndCostume:
			if self.wndCostume.IsShow(): 
				self.wndCostume.Hide()
			else:
				self.wndCostume.Show()
		else:
			self.wndCostume = CostumeWindow(self)
			self.wndCostume.Show()

	def ShowCostumeInventory(self):
		if self.wndCostume :
			if not self.wndCostume.IsShow():
				self.wndCostume.Show()
		else:
			self.wndCostume = CostumeWindow(self)
			self.wndCostume.Show()

	if app.ENABLE_CHEQUE_SYSTEM:
		def OpenPickMoneyDialog(self, focus_idx = 0):
			if mouseModule.mouseController.isAttached():

				attachedSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()
				if playerm2g2.SLOT_TYPE_SAFEBOX == mouseModule.mouseController.GetAttachedType():

					if playerm2g2.ITEM_MONEY == mouseModule.mouseController.GetAttachedItemIndex():
						m2netm2g.SendSafeboxWithdrawMoneyPacket(mouseModule.mouseController.GetAttachedItemCount())
						snd.PlaySound("sound/ui/money.wav")

				mouseModule.mouseController.DeattachObject()

			else:
				curMoney = playerm2g2.GetElk()
				curCheque = playerm2g2.GetCheque()
					
				if curMoney <= 0 and curCheque <= 0:
					return

				self.dlgPickMoney.SetTitleName(localeInfo.PICK_MONEY_TITLE)
				self.dlgPickMoney.SetAcceptEvent(ui.__mem_func__(self.OnPickMoney))
				self.dlgPickMoney.Open(curMoney, curCheque)
				self.dlgPickMoney.SetMax(7) # 인벤토리 990000 제한 버그 수정
				self.dlgPickMoney.SetFocus(focus_idx)
	else:
		def OpenPickMoneyDialog(self):

			if mouseModule.mouseController.isAttached():

				attachedSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()
				if playerm2g2.SLOT_TYPE_SAFEBOX == mouseModule.mouseController.GetAttachedType():

					if playerm2g2.ITEM_MONEY == mouseModule.mouseController.GetAttachedItemIndex():
						m2netm2g.SendSafeboxWithdrawMoneyPacket(mouseModule.mouseController.GetAttachedItemCount())
						snd.PlaySound("sound/ui/money.wav")

				mouseModule.mouseController.DeattachObject()

			else:
				curMoney = playerm2g2.GetElk()

				if curMoney <= 0:
					return

				self.dlgPickMoney.SetTitleName(localeInfo.PICK_MONEY_TITLE)
				self.dlgPickMoney.SetAcceptEvent(ui.__mem_func__(self.OnPickMoney))
				self.dlgPickMoney.Open(curMoney)
				self.dlgPickMoney.SetMax(7) # 인벤토리 990000 제한 버그 수정

	if app.ENABLE_CHEQUE_SYSTEM:
		def OnPickMoney(self, money, cheque):
			mouseModule.mouseController.AttachMoney(self, playerm2g2.SLOT_TYPE_INVENTORY, money, cheque)
	else:
		def OnPickMoney(self, money):
			mouseModule.mouseController.AttachMoney(self, playerm2g2.SLOT_TYPE_INVENTORY, money)

	def OnPickItem(self, count):
		if app.ENABLE_CHEQUE_SYSTEM:
			itemSlotIndex	= self.dlgPickETC.itemGlobalSlotIndex
		else:
			itemSlotIndex	= self.dlgPickMoney.itemGlobalSlotIndex
		
		selectedItemVNum = playerm2g2.GetItemIndex(itemSlotIndex)
		mouseModule.mouseController.AttachObject(self, playerm2g2.SLOT_TYPE_INVENTORY, itemSlotIndex, selectedItemVNum, count)

	def __InventoryLocalSlotPosToGlobalSlotPos(self, local):
		if playerm2g2.IsEquipmentSlot(local) or playerm2g2.IsCostumeSlot(local) or (playerm2g2.IsBeltInventorySlot(local)):
			return local

		return self.inventoryPageIndex*playerm2g2.INVENTORY_PAGE_SIZE + local

	def RefreshBagSlotWindow(self):
		if not self.wndItem:
			return
		
		getItemVNum=playerm2g2.GetItemIndex
		getItemCount=playerm2g2.GetItemCount
		setItemVNum=self.wndItem.SetItemSlot

		## 리프레쉬 하기전에 하이라이트 모두 끈다.
		for i in xrange(self.wndItem.GetSlotCount()):
			self.wndItem.DeactivateSlot(i)
			
		if app.WJ_ENABLE_TRADABLE_ICON or app.ENABLE_MOVE_COSTUME_ATTR:
			if self.interface:
				onTopWindow = self.interface.GetOnTopWindow()
		
		for i in xrange(playerm2g2.INVENTORY_PAGE_SIZE):
			slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)
			
			itemCount = getItemCount(slotNumber)
			# itemCount == 0이면 소켓을 비운다.
			if 0 == itemCount:
				self.wndItem.ClearSlot(i)
				continue
			elif 1 == itemCount:
				itemCount = 0
				
			itemVnum = getItemVNum(slotNumber)
			setItemVNum(i, itemVnum, itemCount)
			
			## 자동물약 (HP: #72723 ~ #72726, SP: #72727 ~ #72730) 특수처리 - 아이템인데도 슬롯에 활성화/비활성화 표시를 위한 작업임 - [hyo]
			if constInfo.IS_AUTO_POTION(itemVnum):
				# metinSocket - [0] : 활성화 여부, [1] : 사용한 양, [2] : 최대 용량
				metinSocket = [playerm2g2.GetItemMetinSocket(slotNumber, j) for j in xrange(playerm2g2.METIN_SOCKET_MAX_NUM)]	
				tempSlotNum = slotNumber
				if tempSlotNum >= playerm2g2.INVENTORY_PAGE_SIZE:
					tempSlotNum -= playerm2g2.INVENTORY_PAGE_SIZE
					
				isActivated = 0 != metinSocket[0]
				
				if isActivated:
					self.wndItem.ActivateSlot(tempSlotNum)
				else:
					self.wndItem.DeactivateSlot(tempSlotNum)
					
			if app.ENABLE_GROWTH_PET_SYSTEM:
				if constInfo.IS_PET_ITEM(itemVnum):
					## 활성된 펫 하이라이트
					self.__ActivePetHighlightSlot(slotNumber)
					
					## 펫 남은 시간에 따라 쿨타임 표시
					self.__SetCollTimePetItemSlot(slotNumber, itemVnum)
					
			if app.WJ_ENABLE_TRADABLE_ICON or app.ENABLE_MOVE_COSTUME_ATTR or app.ENABLE_GROWTH_PET_SYSTEM or app.ENABLE_FISH_EVENT:
				if itemVnum and self.interface and onTopWindow:
					if	self.interface.MarkUnusableInvenSlotOnTopWnd(onTopWindow,slotNumber):
						self.wndItem.SetUnusableSlotOnTopWnd(i)
					else:
						self.wndItem.SetUsableSlotOnTopWnd(i)
				else:
					self.wndItem.SetUsableSlotOnTopWnd(i)

		self.__HighlightSlot_Refresh()
			
		self.wndItem.RefreshSlot()

		if self.wndBelt:
			self.wndBelt.RefreshSlot()

	def RefreshEquipSlotWindow(self):
		getItemVNum=playerm2g2.GetItemIndex
		getItemCount=playerm2g2.GetItemCount
		setItemVNum=self.wndEquip.SetItemSlot
		for i in xrange(playerm2g2.EQUIPMENT_PAGE_COUNT):
			slotNumber = playerm2g2.EQUIPMENT_SLOT_START + i
			itemCount = getItemCount(slotNumber)
			if itemCount <= 1:
				itemCount = 0
			setItemVNum(slotNumber, getItemVNum(slotNumber), itemCount)

		for i in xrange(playerm2g2.NEW_EQUIPMENT_SLOT_COUNT):
			slotNumber = playerm2g2.NEW_EQUIPMENT_SLOT_START + i
			itemCount = getItemCount(slotNumber)
			if itemCount <= 1:
				itemCount = 0
			setItemVNum(slotNumber, getItemVNum(slotNumber), itemCount)

		self.wndEquip.RefreshSlot()
		
		if self.wndCostume:
			self.wndCostume.RefreshCostumeSlot()

	def RefreshItemSlot(self):
		self.RefreshBagSlotWindow()
		self.RefreshEquipSlotWindow()

	def RefreshStatus(self):
		money = playerm2g2.GetElk()
		self.wndMoney.SetText(localeInfo.NumberToMoneyString(money))

		if app.ENABLE_CHEQUE_SYSTEM:
			cheque = playerm2g2.GetCheque()
			self.wndCheque.SetText(str(cheque))
		
	def SetItemToolTip(self, tooltipItem):
		self.tooltipItem = tooltipItem

	def SellItem(self):
		if self.sellingSlotitemIndex == playerm2g2.GetItemIndex(self.sellingSlotNumber):
			if self.sellingSlotitemCount == playerm2g2.GetItemCount(self.sellingSlotNumber):
				## 용혼석도 팔리게 하는 기능 추가하면서 인자 type 추가
				m2netm2g.SendShopSellPacketNew(self.sellingSlotNumber, self.questionDialog.count, playerm2g2.INVENTORY)
				snd.PlaySound("sound/ui/money.wav")
		self.OnCloseQuestionDialog()

	def OnDetachMetinFromItem(self):
		if None == self.questionDialog:
			return
			
		#m2netm2g.SendItemUseToItemPacket(self.questionDialog.sourcePos, self.questionDialog.targetPos)		
		self.__SendUseItemToItemPacket(self.questionDialog.sourcePos, self.questionDialog.targetPos)
		self.OnCloseQuestionDialog()

	def OnCloseQuestionDialog(self):
		if not self.questionDialog:
			return
		
		self.questionDialog.Close()
		self.questionDialog = None
		constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

	## Slot Event
	def SelectEmptySlot(self, selectedSlotPos):
		if constInfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		## 악세서리 창이 열려있으면
		## 아이템 이동 금지.
		if playerm2g2.GetAcceRefineWindowOpen() == 1:
			return
			
		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			if playerm2g2.GetChangeLookWindowOpen() == 1:
				return

		selectedSlotPos = self.__InventoryLocalSlotPosToGlobalSlotPos(selectedSlotPos)

		if mouseModule.mouseController.isAttached():

			attachedSlotType = mouseModule.mouseController.GetAttachedType()
			attachedSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()
			attachedItemCount = mouseModule.mouseController.GetAttachedItemCount()
			attachedItemIndex = mouseModule.mouseController.GetAttachedItemIndex()

			if playerm2g2.SLOT_TYPE_INVENTORY == attachedSlotType:
				if attachedSlotPos>=playerm2g2.DRAGON_SOUL_EQUIPMENT_SLOT_START and attachedSlotPos<playerm2g2.DRAGON_SOUL_EQUIPMENT_SLOT_END:
					mouseModule.mouseController.DeattachObject()
					return
				itemCount = playerm2g2.GetItemCount(attachedSlotPos)
				attachedCount = mouseModule.mouseController.GetAttachedItemCount()
				self.__SendMoveItemPacket(attachedSlotPos, selectedSlotPos, attachedCount)

				if item.IsRefineScroll(attachedItemIndex):
					self.interface.SetUseItemMode(False)

			elif playerm2g2.SLOT_TYPE_PRIVATE_SHOP == attachedSlotType:
				mouseModule.mouseController.RunCallBack("INVENTORY")

			elif playerm2g2.SLOT_TYPE_SHOP == attachedSlotType:
				m2netm2g.SendShopBuyPacket(attachedSlotPos)

			elif playerm2g2.SLOT_TYPE_SAFEBOX == attachedSlotType:

				if playerm2g2.ITEM_MONEY == attachedItemIndex:
					m2netm2g.SendSafeboxWithdrawMoneyPacket(mouseModule.mouseController.GetAttachedItemCount())
					snd.PlaySound("sound/ui/money.wav")

				else:
					m2netm2g.SendSafeboxCheckoutPacket(attachedSlotPos, selectedSlotPos)

			elif playerm2g2.SLOT_TYPE_MALL == attachedSlotType:
				m2netm2g.SendMallCheckoutPacket(attachedSlotPos, selectedSlotPos)
				
			if app.ENABLE_GUILDRENEWAL_SYSTEM:
				# [guild_renewal]
				if playerm2g2.SLOT_TYPE_GUILDBANK == attachedSlotType:
					if playerm2g2.ITEM_MONEY != attachedItemIndex:
						m2netm2g.SendGuildBankCheckOut(attachedSlotPos, selectedSlotPos)

			if playerm2g2.SLOT_TYPE_ACCE == attachedSlotType:
				m2netm2g.SendAcceRefineCheckOut(attachedSlotPos)
				
			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if playerm2g2.SLOT_TYPE_CHANGE_LOOK == attachedSlotType:
					pass
					##m2netm2g.SendAcceRefineCheckOut(attachedSlotPos)

			mouseModule.mouseController.DeattachObject()

	def SelectItemSlot(self, itemSlotIndex):
		if constInfo.GET_ITEM_QUESTION_DIALOG_STATUS() == 1:
			return

		itemSlotIndex = self.__InventoryLocalSlotPosToGlobalSlotPos(itemSlotIndex)

		if mouseModule.mouseController.isAttached():
			attachedSlotType = mouseModule.mouseController.GetAttachedType()
			attachedSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()
			attachedItemVID = mouseModule.mouseController.GetAttachedItemIndex()

			if playerm2g2.SLOT_TYPE_INVENTORY == attachedSlotType:
				if attachedSlotPos>=playerm2g2.DRAGON_SOUL_EQUIPMENT_SLOT_START and attachedSlotPos<playerm2g2.DRAGON_SOUL_EQUIPMENT_SLOT_END:
					mouseModule.mouseController.DeattachObject()
					return
				self.__DropSrcItemToDestItemInInventory(attachedItemVID, attachedSlotPos, itemSlotIndex)

			mouseModule.mouseController.DeattachObject()

		else:
		
			curCursorNum = app.GetCursor()
			if app.SELL == curCursorNum:
				self.__SellItem(itemSlotIndex)
				
			elif app.BUY == curCursorNum:
				chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.SHOP_BUY_INFO)

			elif app.IsPressed(app.DIK_LALT):
				link = playerm2g2.GetItemLink(itemSlotIndex)
				ime.PasteString(link)

			elif app.IsPressed(app.DIK_LSHIFT):
				itemCount = playerm2g2.GetItemCount(itemSlotIndex)
				
				if itemCount > 1:
					if app.ENABLE_CHEQUE_SYSTEM:
						self.dlgPickETC.SetTitleName(localeInfo.PICK_ITEM_TITLE)
						self.dlgPickETC.SetAcceptEvent(ui.__mem_func__(self.OnPickItem))
						self.dlgPickETC.Open(itemCount)
						self.dlgPickETC.itemGlobalSlotIndex  = itemSlotIndex
					else:
						self.dlgPickMoney.SetTitleName(localeInfo.PICK_ITEM_TITLE)
						self.dlgPickMoney.SetAcceptEvent(ui.__mem_func__(self.OnPickItem))
						self.dlgPickMoney.Open(itemCount)
						self.dlgPickMoney.itemGlobalSlotIndex = itemSlotIndex
				#else:
					#selectedItemVNum = playerm2g2.GetItemIndex(itemSlotIndex)
					#mouseModule.mouseController.AttachObject(self, playerm2g2.SLOT_TYPE_INVENTORY, itemSlotIndex, selectedItemVNum)

			elif app.IsPressed(app.DIK_LCONTROL):
				itemIndex = playerm2g2.GetItemIndex(itemSlotIndex)

				if True == item.CanAddToQuickSlotItem(itemIndex):
					playerm2g2.RequestAddToEmptyLocalQuickSlot(playerm2g2.SLOT_TYPE_INVENTORY, itemSlotIndex)
				else:
					chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.QUICKSLOT_REGISTER_DISABLE_ITEM)

			else:
				selectedItemVNum = playerm2g2.GetItemIndex(itemSlotIndex)
				itemCount = playerm2g2.GetItemCount(itemSlotIndex)
				
				if app.ENABLE_GROWTH_PET_SYSTEM:
					if self.__CanAttachGrowthPetItem(selectedItemVNum, itemSlotIndex):
						mouseModule.mouseController.AttachObject(self, playerm2g2.SLOT_TYPE_INVENTORY, itemSlotIndex, selectedItemVNum, itemCount)
				else:	
					mouseModule.mouseController.AttachObject(self, playerm2g2.SLOT_TYPE_INVENTORY, itemSlotIndex, selectedItemVNum, itemCount)
				
				if self.__IsUsableItemToItem(selectedItemVNum, itemSlotIndex):				
					self.interface.SetUseItemMode(True)
				else:					
					self.interface.SetUseItemMode(False)

				snd.PlaySound("sound/ui/pick.wav")

	def __DropSrcItemToDestItemInInventory(self, srcItemVID, srcItemSlotPos, dstItemSlotPos):
		if srcItemSlotPos == dstItemSlotPos:
			return

		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			if playerm2g2.GetChangeLookWindowOpen() == 1:
				return
		
		## 악세서리 창이 열려있으면
		## 아이템 이동 금지.
		if playerm2g2.GetAcceRefineWindowOpen() == 1:
			return

		# cyh itemseal 2013 11 08	
		if item.IsSealScroll(srcItemVID):
			if  playerm2g2.CanSealItem(srcItemVID, playerm2g2.INVENTORY, dstItemSlotPos):
				self.__OpenQuestionDialog(srcItemSlotPos, dstItemSlotPos)
	
		elif item.IsRefineScroll(srcItemVID):
			self.RefineItem(srcItemSlotPos, dstItemSlotPos)
			self.interface.SetUseItemMode(False)

		elif item.IsMetin(srcItemVID):
			self.AttachMetinToItem(srcItemSlotPos, dstItemSlotPos)

		elif item.IsDetachScroll(srcItemVID):
			self.DetachMetinFromItem(srcItemSlotPos, dstItemSlotPos)

		elif item.IsKey(srcItemVID):
			self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)			

		elif (playerm2g2.GetItemFlags(srcItemSlotPos) & ITEM_FLAG_APPLICABLE) == ITEM_FLAG_APPLICABLE:
			self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

		elif item.GetUseType(srcItemVID) in self.USE_TYPE_TUPLE:
			self.__SendUseItemToItemPacket(srcItemSlotPos, dstItemSlotPos)

		else:
			if app.ENABLE_GROWTH_PET_SYSTEM:
				if self.__IsPetItem(srcItemVID):
					if self.__SendUsePetItemToItemPacket(srcItemVID, srcItemSlotPos, dstItemSlotPos):
						return
						
			#snd.PlaySound("sound/ui/drop.wav")
			if item.IsAcceScroll(srcItemVID):
				if playerm2g2.CanAcceClearItem(srcItemVID, playerm2g2.INVENTORY, dstItemSlotPos):
					self.__OpenQuestionDialog(srcItemSlotPos, dstItemSlotPos)
					return
			
			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if item.IsChangeLookClearScroll(srcItemVID):
					if dstItemSlotWindow != playerm2g2.INVENTORY:
						chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.CHANGE_LOOK_DO_NOT_EQUIP_ITEM)
						return
					if playerm2g2.CanChangeLookClearItem(srcItemVID, playerm2g2.INVENTORY, dstItemSlotPos):
						self.__OpenQuestionDialog(srcItemSlotPos, dstItemSlotPos)
						return

			## 이동시킨 곳이 장착 슬롯일 경우 아이템을 사용해서 장착 시킨다 - [levites]
			if playerm2g2.IsEquipmentSlot(dstItemSlotPos):

				## 들고 있는 아이템이 장비일때만
				if item.IsEquipmentVID(srcItemVID):
					self.__UseItem(srcItemSlotPos)

			else:
				self.__SendMoveItemPacket(srcItemSlotPos, dstItemSlotPos, 0)
				#m2netm2g.SendItemMovePacket(srcItemSlotPos, dstItemSlotPos, 0)
				
				
				
	if app.ENABLE_GROWTH_PET_SYSTEM:
		def __OpenPetBagQuestionDialog(self, srcItemSlotPos, dstItemSlotPos):
			if self.interface.IsShowDlgQuestionWindow():
				self.interface.CloseDlgQuestionWindow()
		
		
	if app.ENABLE_GROWTH_PET_SYSTEM:
		def __OpenPetItemQuestionDialog(self, srcItemPos, dstItemPos):
			if self.interface.IsShowDlgQuestionWindow():
				self.interface.CloseDlgQuestionWindow()
			
			getItemVNum=playerm2g2.GetItemIndex
			self.srcItemPos = srcItemPos
			self.dstItemPos = dstItemPos

			srcItemVnum = getItemVNum(srcItemPos)
			dstItemVnum = getItemVNum(dstItemPos)
			
			item.SelectItem( srcItemVnum )
			src_item_name = item.GetItemName( srcItemVnum )
			srcItemType		= item.GetItemType()
			srcItemSubType	= item.GetItemSubType()
			
			item.SelectItem( dstItemVnum )
			dst_item_name = item.GetItemName( getItemVNum(dstItemPos) )
			
			self.PetItemQuestionDlg.SetAcceptEvent(ui.__mem_func__(self.__PetItemAccept))
			self.PetItemQuestionDlg.SetCancelEvent(ui.__mem_func__(self.__PetItemCancel))
			
			if item.ITEM_TYPE_PET == srcItemType:
				if item.PET_FEEDSTUFF == srcItemSubType:
					self.PetItemQuestionDlg.SetText( localeInfo.INVENTORY_REALLY_USE_PET_FEEDSTUFF_ITEM % ( src_item_name, dst_item_name ) )
					self.PetItemQuestionDlg.Open()
				
				elif item.PET_BAG == srcItemSubType:
					self.PetItemQuestionDlg.SetText( localeInfo.INVENTORY_REALLY_USE_PET_BAG_ITEM )
					self.PetItemQuestionDlg.Open()			
			
			
	if app.ENABLE_GROWTH_PET_SYSTEM:		
		def __PetItemAccept(self):
			self.PetItemQuestionDlg.Close()
			self.__SendUseItemToItemPacket(self.srcItemPos, self.dstItemPos)
			self.srcItemPos = (0, 0)
			self.dstItemPos = (0, 0)
			
	if app.ENABLE_GROWTH_PET_SYSTEM:
		def __PetItemCancel(self):
			self.srcItemPos = (0, 0)
			self.dstItemPos = (0, 0)
			self.PetItemQuestionDlg.Close()
				
	def __OpenQuestionDialog(self, srcItemPos, dstItemPos):
		if self.interface.IsShowDlgQuestionWindow():
			self.interface.CloseDlgQuestionWindow()
			
		getItemVNum=playerm2g2.GetItemIndex
		self.srcItemPos = srcItemPos
		self.dstItemPos = dstItemPos
		
		self.dlgQuestion.SetAcceptEvent(ui.__mem_func__(self.__Accept))
		self.dlgQuestion.SetCancelEvent(ui.__mem_func__(self.__Cancel))

		self.dlgQuestion.SetText1("%s" % item.GetItemName(getItemVNum(srcItemPos)) )
		self.dlgQuestion.SetText2(localeInfo.INVENTORY_REALLY_USE_ITEM)

		self.dlgQuestion.Open()
		
	def __Accept(self):
		self.dlgQuestion.Close()
		self.__SendUseItemToItemPacket(self.srcItemPos, self.dstItemPos)
		self.srcItemPos = (0, 0)
		self.dstItemPos = (0, 0)

	def __Cancel(self):
		self.srcItemPos = (0, 0)
		self.dstItemPos = (0, 0)
		self.dlgQuestion.Close()
		
	def __SellItem(self, itemSlotPos):
		if not playerm2g2.IsEquipmentSlot(itemSlotPos):
			self.sellingSlotNumber = itemSlotPos
			itemIndex = playerm2g2.GetItemIndex(itemSlotPos)
			itemCount = playerm2g2.GetItemCount(itemSlotPos)
			
			
			self.sellingSlotitemIndex = itemIndex
			self.sellingSlotitemCount = itemCount

			item.SelectItem(itemIndex)
			## 안티 플레그 검사 빠져서 추가
			## 20140220
			if item.IsAntiFlag(item.ANTIFLAG_SELL):
				popup = uiCommon.PopupDialog()
				popup.SetText(localeInfo.SHOP_CANNOT_SELL_ITEM)
				popup.SetAcceptEvent(self.__OnClosePopupDialog)
				popup.Open()
				self.popup = popup
				return

			itemPrice = item.GetISellItemPrice()

			if item.Is1GoldItem():
				itemPrice = itemCount / itemPrice / 5
			else:
				itemPrice = itemPrice * itemCount / 5

			item.GetItemName(itemIndex)
			itemName = item.GetItemName()

			self.questionDialog = uiCommon.QuestionDialog()
			self.questionDialog.SetText(localeInfo.DO_YOU_SELL_ITEM(itemName, itemCount, itemPrice))
			self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.SellItem))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
			self.questionDialog.Open()
			self.questionDialog.count = itemCount
		
			constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

	def __OnClosePopupDialog(self):
		self.pop = None

	def RefineItem(self, scrollSlotPos, targetSlotPos):

		scrollIndex = playerm2g2.GetItemIndex(scrollSlotPos)
		targetIndex = playerm2g2.GetItemIndex(targetSlotPos)

		if playerm2g2.REFINE_OK != playerm2g2.CanRefine(scrollIndex, targetSlotPos):
			return

		###########################################################
		self.__SendUseItemToItemPacket(scrollSlotPos, targetSlotPos)
		#m2netm2g.SendItemUseToItemPacket(scrollSlotPos, targetSlotPos)
		return
		###########################################################

		###########################################################
		#m2netm2g.SendRequestRefineInfoPacket(targetSlotPos)
		#return
		###########################################################

		result = playerm2g2.CanRefine(scrollIndex, targetSlotPos)

		if playerm2g2.REFINE_ALREADY_MAX_SOCKET_COUNT == result:
			#snd.PlaySound("sound/ui/jaeryun_fail.wav")
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_NO_MORE_SOCKET)

		elif playerm2g2.REFINE_NEED_MORE_GOOD_SCROLL == result:
			#snd.PlaySound("sound/ui/jaeryun_fail.wav")
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_NEED_BETTER_SCROLL)

		elif playerm2g2.REFINE_CANT_MAKE_SOCKET_ITEM == result:
			#snd.PlaySound("sound/ui/jaeryun_fail.wav")
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_SOCKET_DISABLE_ITEM)

		elif playerm2g2.REFINE_NOT_NEXT_GRADE_ITEM == result:
			#snd.PlaySound("sound/ui/jaeryun_fail.wav")
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_UPGRADE_DISABLE_ITEM)

		elif playerm2g2.REFINE_CANT_REFINE_METIN_TO_EQUIPMENT == result:
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_EQUIP_ITEM)

		if playerm2g2.REFINE_OK != result:
			return

		self.refineDialog.Open(scrollSlotPos, targetSlotPos)

	def DetachMetinFromItem(self, scrollSlotPos, targetSlotPos):
		scrollIndex = playerm2g2.GetItemIndex(scrollSlotPos)
		targetIndex = playerm2g2.GetItemIndex(targetSlotPos)

		if not playerm2g2.CanDetach(scrollIndex, targetSlotPos):
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_METIN_INSEPARABLE_ITEM)
			return

		self.questionDialog = uiCommon.QuestionDialog()
		self.questionDialog.SetText(localeInfo.REFINE_DO_YOU_SEPARATE_METIN)
		self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.OnDetachMetinFromItem))
		self.questionDialog.SetCancelEvent(ui.__mem_func__(self.OnCloseQuestionDialog))
		self.questionDialog.Open()
		self.questionDialog.sourcePos = scrollSlotPos
		self.questionDialog.targetPos = targetSlotPos

	def AttachMetinToItem(self, metinSlotPos, targetSlotPos):
		metinIndex = playerm2g2.GetItemIndex(metinSlotPos)
		targetIndex = playerm2g2.GetItemIndex(targetSlotPos)

		item.SelectItem(metinIndex)
		itemName = item.GetItemName()

		result = playerm2g2.CanAttachMetin(metinIndex, targetSlotPos)

		if playerm2g2.ATTACH_METIN_NOT_MATCHABLE_ITEM == result:
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_CAN_NOT_ATTACH(itemName))

		if playerm2g2.ATTACH_METIN_NO_MATCHABLE_SOCKET == result:
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_NO_SOCKET(itemName))

		elif playerm2g2.ATTACH_METIN_NOT_EXIST_GOLD_SOCKET == result:
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_NO_GOLD_SOCKET(itemName))

		elif playerm2g2.ATTACH_METIN_CANT_ATTACH_TO_EQUIPMENT == result:
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.REFINE_FAILURE_EQUIP_ITEM)

		if playerm2g2.ATTACH_METIN_OK != result:
			return

		self.attachMetinDialog.Open(metinSlotPos, targetSlotPos)


		
	def OverOutItem(self):
		self.wndItem.SetUsableItem(False)
		if None != self.tooltipItem:
			self.tooltipItem.HideToolTip()

	def OverInItem(self, overSlotPos):
		if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
			overInvenSlotPos = self.__InventoryLocalSlotPosToGlobalSlotPos(overSlotPos)
			self.wndItem.SetUsableItem(False)

			getItemVNum = playerm2g2.GetItemIndex
			itemVnum = getItemVNum(overInvenSlotPos)
			self.DelHighlightSlot(overInvenSlotPos)

			if mouseModule.mouseController.isAttached():
				attachedItemType = mouseModule.mouseController.GetAttachedType()
				if playerm2g2.SLOT_TYPE_INVENTORY == attachedItemType:

					attachedSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()
					attachedItemVNum = mouseModule.mouseController.GetAttachedItemIndex()
					
					if self.__CanUseSrcItemToDstItem(attachedItemVNum, attachedSlotPos, overInvenSlotPos):
						self.wndItem.SetUsableItem(True)
						self.ShowToolTip(overInvenSlotPos)
						return
					
			self.ShowToolTip(overInvenSlotPos)
		else:
			overSlotPos = self.__InventoryLocalSlotPosToGlobalSlotPos(overSlotPos)
			self.wndItem.SetUsableItem(False)

			if mouseModule.mouseController.isAttached():
				attachedItemType = mouseModule.mouseController.GetAttachedType()
				if playerm2g2.SLOT_TYPE_INVENTORY == attachedItemType:

					attachedSlotPos = mouseModule.mouseController.GetAttachedSlotNumber()
					attachedItemVNum = mouseModule.mouseController.GetAttachedItemIndex()
					
					if self.__CanUseSrcItemToDstItem(attachedItemVNum, attachedSlotPos, overSlotPos):
						self.wndItem.SetUsableItem(True)
						self.ShowToolTip(overSlotPos)
						return
					
			self.ShowToolTip(overSlotPos)


	def __IsUsableItemToItem(self, srcItemVNum, srcSlotPos):
		"다른 아이템에 사용할 수 있는 아이템인가?"

		if item.IsRefineScroll(srcItemVNum):
			return True
		elif item.IsSealScroll(srcItemVNum):
			return True
		elif item.IsMetin(srcItemVNum):
			return True
		elif item.IsDetachScroll(srcItemVNum):
			return True
		elif item.IsKey(srcItemVNum):
			return True
		elif item.IsItemUsedForDragonSoul(srcItemVNum):
			return True
		elif (playerm2g2.GetItemFlags(srcSlotPos) & ITEM_FLAG_APPLICABLE) == ITEM_FLAG_APPLICABLE:
			return True
		else:
			if app.ENABLE_GROWTH_PET_SYSTEM:
				if self.__IsUsablePetItem(srcItemVNum):
					return True
					
			if item.IsAcceScroll(srcItemVNum):
				return True
				
			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if item.IsChangeLookClearScroll(srcItemVNum):
					return True

			if item.GetUseType(srcItemVNum) in self.USE_TYPE_TUPLE:
				return True
			
		return False

	def __CanUseSrcItemToDstItem(self, srcItemVNum, srcSlotPos, dstSlotPos):
		"대상 아이템에 사용할 수 있는가?"
		if srcSlotPos == dstSlotPos:
			return False

		if item.IsRefineScroll(srcItemVNum):
			if playerm2g2.REFINE_OK == playerm2g2.CanRefine(srcItemVNum, dstSlotPos):
				return True
		elif item.IsSealScroll(srcItemVNum):
			if playerm2g2.CanSealItem(srcItemVNum, playerm2g2.INVENTORY, dstSlotPos):
				return True
		elif item.IsMetin(srcItemVNum):
			if playerm2g2.ATTACH_METIN_OK == playerm2g2.CanAttachMetin(srcItemVNum, dstSlotPos):
				return True
		elif item.IsDetachScroll(srcItemVNum):
			if playerm2g2.DETACH_METIN_OK == playerm2g2.CanDetach(srcItemVNum, dstSlotPos):
				return True
		elif item.IsKey(srcItemVNum):
			if playerm2g2.CanUnlock(srcItemVNum, dstSlotPos):
				return True
		elif (playerm2g2.GetItemFlags(srcSlotPos) & ITEM_FLAG_APPLICABLE) == ITEM_FLAG_APPLICABLE:
			return True
		else:
			if app.ENABLE_GROWTH_PET_SYSTEM:
				if self.__CanUseSrcPetItemToDstPetItem(srcItemVNum, srcSlotPos, dstSlotPos):
					return True
					
			if item.IsAcceScroll(srcItemVNum):
				if playerm2g2.CanAcceClearItem(srcItemVNum, playerm2g2.INVENTORY, dstSlotPos):
					return True
					
			if app.ENABLE_CHANGE_LOOK_SYSTEM:
				if playerm2g2.CanChangeLookClearItem(srcItemVNum, playerm2g2.INVENTORY, dstSlotPos):
					return True

			useType=item.GetUseType(srcItemVNum)

			if "USE_CLEAN_SOCKET" == useType:
				if self.__CanCleanBrokenMetinStone(dstSlotPos):
					return True
			elif "USE_CHANGE_ATTRIBUTE" == useType:
				if self.__CanChangeItemAttrList(dstSlotPos):
					return True
			elif "USE_ADD_ATTRIBUTE" == useType:
				if self.__CanAddItemAttr(dstSlotPos):
					return True
			elif "USE_ADD_ATTRIBUTE2" == useType:
				if self.__CanAddItemAttr(dstSlotPos):
					return True
			elif "USE_ADD_ACCESSORY_SOCKET" == useType:
				if self.__CanAddAccessorySocket(dstSlotPos):
					return True
			elif "USE_PUT_INTO_ACCESSORY_SOCKET" == useType:								
				if self.__CanPutAccessorySocket(dstSlotPos, srcItemVNum):
					return TRUE;
			elif "USE_PUT_INTO_BELT_SOCKET" == useType:								
				dstItemVNum = playerm2g2.GetItemIndex(dstSlotPos)

				item.SelectItem(dstItemVNum)
		
				if item.ITEM_TYPE_BELT == item.GetItemType():
					return True
			elif "USE_CHANGE_COSTUME_ATTR" == useType:
				if self.__CanChangeCostumeAttrList(dstSlotPos):
					return True
			elif "USE_RESET_COSTUME_ATTR" == useType:
				if self.__CanResetCostumeAttr(dstSlotPos):
					return True
			else :
				if app.ENABLE_CHANGED_ATTR :
					if "USE_SELECT_ATTRIBUTE" == useType:
						if self.__CanChangeItemAttrList(dstSlotPos):
							return True
				else:
					pass
					
		return False

	def __CanCleanBrokenMetinStone(self, dstSlotPos):
		dstItemVNum = playerm2g2.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)
		
		if item.ITEM_TYPE_WEAPON != item.GetItemType():
			return False

		for i in xrange(playerm2g2.METIN_SOCKET_MAX_NUM):
			if playerm2g2.GetItemMetinSocket(dstSlotPos, i) == constInfo.ERROR_METIN_STONE:
				return True

		return False

	def __CanChangeItemAttrList(self, dstSlotPos):
		dstItemVNum = playerm2g2.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)
		
		if not item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):	 
			return False
			
		# 재경비서
		if app.ENABLE_NEW_USER_CARE:
			if item.IsAntiFlag(item.ITEM_ANTIFLAG_ENCHANT):
				return False

		for i in xrange(playerm2g2.METIN_SOCKET_MAX_NUM):
			if playerm2g2.GetItemAttribute(dstSlotPos, i) != 0:
				return True

		return False

	def __CanPutAccessorySocket(self, dstSlotPos, mtrlVnum):
		dstItemVNum = playerm2g2.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if item.GetItemType() != item.ITEM_TYPE_ARMOR:
			return False

		if not item.GetItemSubType() in (item.ARMOR_WRIST, item.ARMOR_NECK, item.ARMOR_EAR):
			return False

		curCount = playerm2g2.GetItemMetinSocket(dstSlotPos, 0)
		maxCount = playerm2g2.GetItemMetinSocket(dstSlotPos, 1)

		if mtrlVnum != constInfo.GET_ACCESSORY_MATERIAL_VNUM(dstItemVNum, item.GetItemSubType()):
			return False
		
		if curCount>=maxCount:
			return False

		return True

	def __CanAddAccessorySocket(self, dstSlotPos):
		dstItemVNum = playerm2g2.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)

		if item.GetItemType() != item.ITEM_TYPE_ARMOR:
			return False

		if not item.GetItemSubType() in (item.ARMOR_WRIST, item.ARMOR_NECK, item.ARMOR_EAR):
			return False

		curCount = playerm2g2.GetItemMetinSocket(dstSlotPos, 0)
		maxCount = playerm2g2.GetItemMetinSocket(dstSlotPos, 1)
		
		ACCESSORY_SOCKET_MAX_SIZE = 3
		if maxCount >= ACCESSORY_SOCKET_MAX_SIZE:
			return False

		return True

	def __CanAddItemAttr(self, dstSlotPos):
		dstItemVNum = playerm2g2.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False

		item.SelectItem(dstItemVNum)
		
		if not item.GetItemType() in (item.ITEM_TYPE_WEAPON, item.ITEM_TYPE_ARMOR):	 
			return False
			
		# 재가비서
		if app.ENABLE_NEW_USER_CARE:
			if item.IsAntiFlag(item.ITEM_ANTIFLAG_REINFORCE):
				return False
			
		attrCount = 0
		for i in xrange(playerm2g2.METIN_SOCKET_MAX_NUM):
			if playerm2g2.GetItemAttribute(dstSlotPos, i) != 0:
				attrCount += 1

		if attrCount<4:
			return True
								
		return False

	def __CanChangeCostumeAttrList(self, dstSlotPos):
		dstItemVNum = playerm2g2.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False
		
		item.SelectItem(dstItemVNum)
		
		if item.GetItemType() !=item.ITEM_TYPE_COSTUME:	 
			return False
		
		if item.GetItemSubType() == item.COSTUME_TYPE_ACCE:
			return False
		
		if item.GetItemSubType() == item.COSTUME_TYPE_MOUNT:
			return False	  
		
		for i in xrange(playerm2g2.METIN_SOCKET_MAX_NUM):
			type, value = playerm2g2.GetItemAttribute(dstSlotPos, i)
			if type != 0:
				return True
		
		return False
	
	def __CanResetCostumeAttr(self, dstSlotPos):
		dstItemVNum = playerm2g2.GetItemIndex(dstSlotPos)
		if dstItemVNum == 0:
			return False
		
		item.SelectItem(dstItemVNum)
		
		if item.GetItemType() !=item.ITEM_TYPE_COSTUME:	 	  
			return False
		
		if item.GetItemSubType() == item.COSTUME_TYPE_ACCE:
			return False
		
		if item.GetItemSubType() == item.COSTUME_TYPE_MOUNT:
			return False	 
		
		for i in xrange(playerm2g2.METIN_SOCKET_MAX_NUM):
			type, value = playerm2g2.GetItemAttribute(dstSlotPos, i)
			if type != 0:
				return True
		
		return False
		
	
	def ShowToolTip(self, slotIndex):
		if None != self.tooltipItem:
			self.tooltipItem.SetInventoryItem(slotIndex)

	def OnTop(self):
		if None != self.tooltipItem:
			self.tooltipItem.SetTop()

	def OnPressEscapeKey(self):
		self.Close()
		return True

	def UseItemSlot(self, slotIndex):
	
		if app.ENABLE_FISH_EVENT:
			if mouseModule.mouseController.isAttached():
				if playerm2g2.SLOT_TYPE_FISH_EVENT == mouseModule.mouseController.GetAttachedType():
					return
					
					
		curCursorNum = app.GetCursor()
		if app.SELL == curCursorNum:
			return

		if constInfo.GET_ITEM_QUESTION_DIALOG_STATUS():
			return

		slotIndex = self.__InventoryLocalSlotPosToGlobalSlotPos(slotIndex)

		if self.wndDragonSoulRefine.IsShow():
			self.wndDragonSoulRefine.AutoSetItem((playerm2g2.INVENTORY, slotIndex), 1)
			return

		self.__UseItem(slotIndex)
		mouseModule.mouseController.DeattachObject()
		self.OverOutItem()

	def __UseItem(self, slotIndex):
		ItemVNum = playerm2g2.GetItemIndex(slotIndex)
		item.SelectItem(ItemVNum)		
					
		## 악세서리 창이 열려있으면
		## 악세서리 아이템, 무기, 갑옷 외엔 아무 사용 안됨.
		if playerm2g2.GetAcceRefineWindowOpen() == 1:
			self.__UseItemAcce(slotIndex)
			return
			
		if app.ENABLE_CHANGE_LOOK_SYSTEM:
			if playerm2g2.GetChangeLookWindowOpen() == 1:
				return
		
		if app.WJ_ENABLE_TRADABLE_ICON or app.ENABLE_MOVE_COSTUME_ATTR or app.ENABLE_GROWTH_PET_SYSTEM:
			if self.interface.AttachInvenItemToOtherWindowSlot(slotIndex):
				return
				
		if app.ENABLE_GROWTH_PET_SYSTEM:		
			itemType = item.GetItemType()
			if item.ITEM_TYPE_PET == itemType:
				self.__UseItemPet(slotIndex)
				return

		if item.IsFlag(item.ITEM_FLAG_CONFIRM_WHEN_USE):
			self.questionDialog = uiCommon.QuestionDialog()
			if app.ENABLE_12ZI:
				self.questionDialog.SetText(self.GetConfirmQuestion(ItemVNum))
				(width, height) = self.questionDialog.GetTextSize()
				self.questionDialog.SetWidth(width+16)
			else:
				self.questionDialog.SetText(localeInfo.INVENTORY_REALLY_USE_ITEM2)
				
			self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnAccept))
			self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnCancel))
			self.questionDialog.Open()
			self.questionDialog.slotIndex = slotIndex
		
			constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)
		else:
			self.__SendUseItemPacket(slotIndex)
			#m2netm2g.SendItemUsePacket(slotIndex)	

	if app.ENABLE_12ZI:
		def GetConfirmQuestion(self, vnum):
			item.SelectItem(vnum)
			if vnum == 72327 or vnum == 72329:
				return localeInfo.CHARGE_BEAD_QUESTION % (item.GetValue(0))
			elif vnum == 72328:
				return localeInfo.UNLIMIT_ENTER_CZ_QUESTION % (item.GetValue(0))
			else:
				return localeInfo.INVENTORY_REALLY_USE_ITEM2

	if app.ENABLE_GROWTH_PET_SYSTEM:
		##펫 UseItemPet
		def __UseItemPet(self, slotIndex):
			itemSubType = item.GetItemSubType()		
			if item.PET_EGG == itemSubType:
				self.petHatchingWindow.HatchingWindowOpen(playerm2g2.INVENTORY, slotIndex)
				
			elif item.PET_UPBRINGING == itemSubType:
				if playerm2g2.CanUsePetCoolTimeCheck():
					if self.__CanUseGrowthPet(slotIndex):
						self.__SendUseItemPacket(slotIndex)
						
			elif item.PET_BAG == itemSubType:
				if self.__CanUsePetBagItem(slotIndex):
					if self.questionDialog:
						self.questionDialog.Close()
						
					self.questionDialog = uiCommon.QuestionDialog()
					self.questionDialog.SetText(localeInfo.INVENTORY_REALLY_USE_PET_BAG_TAKE_OUT)
					self.questionDialog.SetAcceptEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnAccept))
					self.questionDialog.SetCancelEvent(ui.__mem_func__(self.__UseItemQuestionDialog_OnCancel))
					self.questionDialog.slotIndex = slotIndex
					self.questionDialog.Open()
					
	if app.ENABLE_GROWTH_PET_SYSTEM:		
		##펫 ITEM_FLAG_CONFIRM_WHEN_USE 플래그가 버그가 있어 만듬
		## 아이템 사용시 다이얼로그 창을 띄워서 사용여부를 두줄 출력하여 물어봄.
		## 첫줄 : 아이템명, 두번째줄 : localeInfo.INVENTORY_REALLY_USE_ITEM
		def __OpenQuestionDialog2(self, slotIndex):
			if self.interface.IsShowDlgQuestionWindow():
				self.interface.CloseDlgQuestionWindow()
			
			self.OpenQuestionDialog2SlotIndex = slotIndex
			self.dlgQuestion.SetAcceptEvent(ui.__mem_func__(self.__QuestionDialog2Accept))
			self.dlgQuestion.SetCancelEvent(ui.__mem_func__(self.__QuestionDialog2Cancel))
			
			self.dlgQuestion.SetText1("%s" % item.GetItemName(playerm2g2.GetItemIndex(slotIndex)) )
			self.dlgQuestion.SetText2(localeInfo.INVENTORY_REALLY_USE_ITEM)

			self.dlgQuestion.Open()
			
	if app.ENABLE_GROWTH_PET_SYSTEM:	
		def __QuestionDialog2Accept(self):
			self.dlgQuestion.Close()
			self.__SendUseItemPacket(self.OpenQuestionDialog2SlotIndex)
			self.OpenQuestionDialog2SlotIndex = (0, 0)
	
	if app.ENABLE_GROWTH_PET_SYSTEM:	
		def __QuestionDialog2Cancel(self):
			self.OpenQuestionDialog2SlotIndex = (0, 0)
			self.dlgQuestion.Close()
			
	def __UseItemAcce(self, slotIndex):

		AcceSlot = playerm2g2.FineMoveAcceItemSlot()
		UsingAcceSlot = playerm2g2.FindActivedAcceSlot(slotIndex)
		if slotIndex > playerm2g2.EQUIPMENT_SLOT_START-1: ## 인벤창 안에 있는 것만.
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.ACCE_NOT_USINGITEM)
			return

		## 봉인아이템 걸러냄
		if playerm2g2.GetItemSealDate(playerm2g2.INVENTORY, slotIndex) != -1:
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.ACCE_NOT_SEALITEM)
			return

		## 조합창
		if playerm2g2.GetAcceRefineWindowType() == playerm2g2.ACCE_SLOT_TYPE_COMBINE:
			if item.GetItemType() == item.ITEM_TYPE_COSTUME:
				if item.GetItemSubType() == item.COSTUME_TYPE_ACCE:
					if app.ENABLE_ACCE_SECOND_COSTUME_SYSTEM:
						## 전설등급 최고 흡수율 25%
						socketInDrainValue = playerm2g2.GetItemMetinSocket(slotIndex, 1)
						if socketInDrainValue >= app.ACCE_MAX_DRAINRATE:
							chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.ACCE_MAX_DRAINRATE)
							return
					else:
						if item.GetRefinedVnum() == 0: ## 전선등급 아이템은 걸러냄.
							chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.ACCE_MAXGRADE)
							return

					if UsingAcceSlot == playerm2g2.ACCE_SLOT_MAX:
						if AcceSlot != playerm2g2.ACCE_SLOT_MAX:
							if not playerm2g2.FindUsingAcceSlot(AcceSlot) == playerm2g2.ITEM_SLOT_COUNT:
								return
							if playerm2g2.FindUsingAcceSlot(playerm2g2.ACCE_SLOT_LEFT) == playerm2g2.ITEM_SLOT_COUNT:
								if AcceSlot == playerm2g2.ACCE_SLOT_RIGHT:
									return
							playerm2g2.SetAcceActivedItemSlot(AcceSlot, slotIndex)
							m2netm2g.SendAcceRefineCheckIn(playerm2g2.INVENTORY, slotIndex, AcceSlot, playerm2g2.GetAcceRefineWindowType())
				else:
					chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.ACCE_POSSIBLE_ACCE)
					return
			else:
				chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.ACCE_POSSIBLE_ACCE)
				return
			
		## 흡수창
		elif playerm2g2.GetAcceRefineWindowType() == playerm2g2.ACCE_SLOT_TYPE_ABSORB:
			isAbsorbItem = 0
			if item.GetItemType() == item.ITEM_TYPE_COSTUME:
				if item.GetItemSubType() == item.COSTUME_TYPE_ACCE:
					if not playerm2g2.GetItemMetinSocket(slotIndex,0) == 0:
						chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.ACCE_NOTABSORBITEM)
						return
					if UsingAcceSlot == playerm2g2.ACCE_SLOT_MAX:
						if not AcceSlot == playerm2g2.ACCE_SLOT_LEFT: ## 악세서리아이템은 왼쪽 슬롯에만
							return
						playerm2g2.SetAcceActivedItemSlot(AcceSlot, slotIndex)
						m2netm2g.SendAcceRefineCheckIn(playerm2g2.INVENTORY, slotIndex, AcceSlot, playerm2g2.GetAcceRefineWindowType())
				else:
					chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.ACCE_POSSIBLE_ACCEITEM)
					return	
					
			elif item.GetItemType() == item.ITEM_TYPE_WEAPON: ## 무기류.
				isAbsorbItem = 1
				
			elif item.GetItemType() == item.ITEM_TYPE_ARMOR: ## 갑옷류
				if item.GetItemSubType() == item.ARMOR_BODY:
					isAbsorbItem = 1
				else:
					chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.ACCE_POSSIBLE_ACCEITEM)
					return
			else:
				chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.ACCE_POSSIBLE_ACCEITEM)
				return				

			if localeInfo.IsBRAZIL():
				## 브라질에서 아래 나열된 아이템은 능력치가 상당히 강해서 흡수 안되게 해달라고 조름.
				## 어쩔수 없이 하드코딩함. 
				itemvnum = item.GetVnum()
				if itemvnum == 11979 or itemvnum == 11980 or itemvnum == 11981 or itemvnum == 11982 or itemvnum == 11971 or itemvnum == 11972 or itemvnum == 11973 or itemvnum == 11974:
					chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.ACCE_DONOT_ABSORDITEM)
					return

			if app.ENABLE_ACCE_SECOND_COSTUME_SYSTEM:
				itemvnum = item.GetVnum()
				if item.IsWedddingItem(itemvnum) == 1:
					chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.ACCE_POSSIBLE_ACCEITEM)
					return

			if isAbsorbItem:
				if UsingAcceSlot == playerm2g2.ACCE_SLOT_MAX:
					if not AcceSlot == playerm2g2.ACCE_SLOT_RIGHT: ## 흡수될 아이템은 오른쪽 슬롯에만
						if playerm2g2.FindUsingAcceSlot(playerm2g2.ACCE_SLOT_RIGHT) == playerm2g2.ITEM_SLOT_COUNT:
							AcceSlot = playerm2g2.ACCE_SLOT_RIGHT
						else:	
							return

					popup = uiCommon.QuestionDialog()
					popup.SetText(localeInfo.ACCE_DEL_ABSORDITEM)
					popup.SetAcceptEvent(lambda arg1=slotIndex, arg2=AcceSlot: self.OnAcceAcceptEvent(arg1, arg2))
					popup.SetCancelEvent(self.OnAcceCloseEvent)
					popup.Open()
					self.pop = popup
					
		## 경고 메시지 띄우기.
		if not playerm2g2.FindUsingAcceSlot(playerm2g2.ACCE_SLOT_RIGHT) == playerm2g2.ITEM_SLOT_COUNT and not playerm2g2.FindUsingAcceSlot(playerm2g2.ACCE_SLOT_LEFT) == playerm2g2.ITEM_SLOT_COUNT:
			if AcceSlot != playerm2g2.ACCE_SLOT_MAX:
				popup = uiCommon.PopupDialog()
				if playerm2g2.GetAcceRefineWindowType() == playerm2g2.ACCE_SLOT_TYPE_COMBINE:
					
					if app.ENABLE_ACCE_SECOND_COSTUME_SYSTEM:
						socketInDrainValue = playerm2g2.GetAcceItemMetinSocket(0, 1)
						socketInDrainValue2 = playerm2g2.GetAcceItemMetinSocket(1, 1)
						socketInDrainValue3 = playerm2g2.GetItemMetinSocket(slotIndex, 1)
						## 메인 서버 중. 등록된 아이템이 전설일때 경고 메시지 변경.
						if socketInDrainValue > 0 or socketInDrainValue2 > 0 or socketInDrainValue3 > 0:
							popup.SetText(localeInfo.ACCE_DEL_SERVEITEM2)
						else:
							popup.SetText(localeInfo.ACCE_DEL_SERVEITEM)
					else:
						popup.SetText(localeInfo.ACCE_DEL_SERVEITEM)
					
					popup.SetAcceptEvent(self.__OnClosePopupDialog)
					popup.Open()
					self.pop = popup

	## 아이템 흡수시 흡수될 아이템 할지 안할지 선택 팝업
	def OnAcceAcceptEvent(self, slotIndex, AcceSlot):
		self.pop.Close()
		self.pop = None
		playerm2g2.SetAcceActivedItemSlot(AcceSlot, slotIndex)
		m2netm2g.SendAcceRefineCheckIn(playerm2g2.INVENTORY, slotIndex, AcceSlot, playerm2g2.GetAcceRefineWindowType())

	def OnAcceCloseEvent(self):
		self.pop.Close()
		self.pop = None
						
	def __UseItemQuestionDialog_OnCancel(self):
		self.OnCloseQuestionDialog()

	def __UseItemQuestionDialog_OnAccept(self):
		self.__SendUseItemPacket(self.questionDialog.slotIndex)
		self.OnCloseQuestionDialog()		

	def __SendUseItemToItemPacket(self, srcSlotPos, dstSlotPos):
		# 개인상점 열고 있는 동안 아이템 사용 방지
		if uiPrivateShopBuilder.IsBuildingPrivateShop():
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.USE_ITEM_FAILURE_PRIVATE_SHOP)
			return
		
		if self.interface.IsShowDlgQuestionWindow():
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.DONT_USE_ITEM_WHEN_SHOW_CONFIRM)
			return
			
		m2netm2g.SendItemUseToItemPacket(srcSlotPos, dstSlotPos)

	def __SendUseItemPacket(self, slotPos):
		# 개인상점 열고 있는 동안 아이템 사용 방지
		if uiPrivateShopBuilder.IsBuildingPrivateShop():
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.USE_ITEM_FAILURE_PRIVATE_SHOP)
			return
		
		if self.interface.IsShowDlgQuestionWindow():
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.DONT_USE_ITEM_WHEN_SHOW_CONFIRM)
			return
			
		m2netm2g.SendItemUsePacket(slotPos)
	
	def __SendMoveItemPacket(self, srcSlotPos, dstSlotPos, srcItemCount):
		# 개인상점 열고 있는 동안 아이템 사용 방지
		if uiPrivateShopBuilder.IsBuildingPrivateShop():
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.MOVE_ITEM_FAILURE_PRIVATE_SHOP)
			return
		
		if self.interface.IsShowDlgQuestionWindow():
			chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.DONT_USE_ITEM_WHEN_SHOW_CONFIRM)
			return

		m2netm2g.SendItemMovePacket(srcSlotPos, dstSlotPos, srcItemCount)
	
	def SetDragonSoulRefineWindow(self, DragonSoulRefine):
		self.wndDragonSoulRefine = DragonSoulRefine
			
	def OnMoveWindow(self, x, y):
		if self.wndBelt:
			self.wndBelt.AdjustPositionAndSize()

	# 악세서리 슬롯 테두리 추가, 제거.
	def DeactivateSlot(self, slotindex):
		self.__DelHighlightSlotAcce(slotindex)

	def ActivateSlot(self, slotindex):
		self.__AddHighlightSlotAcce(slotindex)
		
	## 악세서리 용 하이라이트 list 추가.
	def __AddHighlightSlotAcce(self, slotIndex):
		if not slotIndex in self.listHighlightedAcceSlot:
			self.listHighlightedAcceSlot.append(slotIndex)
			
	## 악세서리 용 하이라이트 list 삭제.
	def __DelHighlightSlotAcce(self, slotIndex):
		if slotIndex in self.listHighlightedAcceSlot:
			
			if slotIndex >= playerm2g2.INVENTORY_PAGE_SIZE:
				self.wndItem.DeactivateSlot(slotIndex-playerm2g2.INVENTORY_PAGE_SIZE)
			else:
				self.wndItem.DeactivateSlot(slotIndex)

			self.listHighlightedAcceSlot.remove(slotIndex)

	## 하이라이트 리프레쉬.		
	def __HighlightSlot_Refresh(self):
		## 악세서리.
		for i in xrange(self.wndItem.GetSlotCount()):
			slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)
			if slotNumber in self.listHighlightedAcceSlot:
				self.wndItem.ActivateSlot(i)
				## 악세서리 용은 테두리 색 녹색으로 변경한다.
				self.wndItem.SetSlotDiffuseColor(i, wndMgr.COLOR_TYPE_GREEN)

		## 초반개선 하이라이트
		if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
			for i in xrange(self.wndItem.GetSlotCount()):
				slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)
				if slotNumber in self.listHighlightedSlot:
					self.wndItem.ActivateSlot(i)
	
	## 악세서리 용 하이라이트 list 클리어.
	def __HighlightSlot_Clear(self):
		## 악세서리
		for i in xrange(self.wndItem.GetSlotCount()):
			slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)
			if slotNumber in self.listHighlightedAcceSlot:
				self.wndItem.DeactivateSlot(i)
				self.listHighlightedAcceSlot.remove(slotNumber)
		## 초반개선 하이라이트
		if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
			for i in xrange(self.wndItem.GetSlotCount()):
				slotNumber = self.__InventoryLocalSlotPosToGlobalSlotPos(i)
				if slotNumber in self.listHighlightedSlot:
					self.wndItem.DeactivateSlot(i)
					self.listHighlightedSlot.remove(slotNumber)

							
	if app.WJ_ENABLE_PICKUP_ITEM_EFFECT:
		# 슬롯 highlight 관련
		## 추가
		def HighlightSlot(self, slot):
			#slot값에 대한 예외처리.
			if slot>playerm2g2.INVENTORY_PAGE_SIZE*playerm2g2.INVENTORY_PAGE_COUNT:
				return
			
			if not slot in self.listHighlightedSlot:
				self.listHighlightedSlot.append (slot)
		## 삭제
		def DelHighlightSlot(self, inventorylocalslot):
			if inventorylocalslot in self.listHighlightedSlot:
				if inventorylocalslot >= playerm2g2.INVENTORY_PAGE_SIZE:
					self.wndItem.DeactivateSlot(inventorylocalslot-playerm2g2.INVENTORY_PAGE_SIZE)
				else:
					self.wndItem.DeactivateSlot(inventorylocalslot)

				self.listHighlightedSlot.remove(inventorylocalslot)
		
		# 슬롯 highlight 관련 끝
	
	# wj.2014.12.2. 인벤토리와 DS인벤 간의 상태를 확인 및 설정하기 위한 함수.
	def IsDlgQuestionShow(self):
		if self.dlgQuestion.IsShow():
			return True
		else:
			return False
	
	def CancelDlgQuestion(self):
		self.__Cancel()
	
	def SetUseItemMode(self, bUse):
		self.wndItem.SetUseMode(bUse)
	
	if app.ENABLE_GROWTH_PET_SYSTEM:			
		## 활성한 펫 하이라이트 표시
		def __ActivePetHighlightSlot(self, slotNumber):
			active_id	= playerm2g2.GetActivePetItemId()
			
			if active_id == 0:
				return
				
			if active_id == playerm2g2.GetItemMetinSocket(playerm2g2.INVENTORY, slotNumber, 2):  ## 0 ~ 89
				
				if slotNumber >= playerm2g2.INVENTORY_PAGE_SIZE:
					slotNumber -= playerm2g2.INVENTORY_PAGE_SIZE
			
				self.wndItem.ActivateSlot(slotNumber)	## 0 ~ 44
				
	if app.ENABLE_GROWTH_PET_SYSTEM:		
		## 남은 시간에 따른 쿨타임 표시( slotNumber 는 0 ~ 89 )
		def __SetCollTimePetItemSlot(self, slotNumber, itemVnum):
		
			item.SelectItem(itemVnum)
			itemSubType = item.GetItemSubType()
		
			if itemSubType not in [item.PET_UPBRINGING, item.PET_BAG]:
				return
				
			if itemSubType == item.PET_BAG:
				id = playerm2g2.GetItemMetinSocket(playerm2g2.INVENTORY, slotNumber, 2)
				if id == 0:
					return
			
			(limitType, limitValue) = item.GetLimit(0)
			
			#육성펫의 LimitValue 는 1번 소켓에 있다.
			if itemSubType == item.PET_UPBRINGING:
				limitValue = playerm2g2.GetItemMetinSocket(playerm2g2.INVENTORY, slotNumber, 1)
					
			if limitType in [item.LIMIT_REAL_TIME, item.LIMIT_REAL_TIME_START_FIRST_USE]:
								
				sock_time   = playerm2g2.GetItemMetinSocket(playerm2g2.INVENTORY, slotNumber, 0)
				
				remain_time = max( 0, sock_time - app.GetGlobalTimeStamp() )
				
				if slotNumber >= playerm2g2.INVENTORY_PAGE_SIZE:
					slotNumber -= playerm2g2.INVENTORY_PAGE_SIZE

				## SetSlotCoolTimeInverse 의 slotNumber는 0 ~ 44
				self.wndItem.SetSlotCoolTimeInverse(slotNumber, limitValue, limitValue - remain_time)
				
				#print "item Limit TYPE: ", limitType
				#print "item Limit VALUE: ", limitValue	
				#print "남은 시간 : ", remain_time
				#print "경과 시간 : ", limitValue - remain_time
			
	if app.ENABLE_GROWTH_PET_SYSTEM or app.ENABLE_MOVE_COSTUME_ATTR:		
		def GetInventoryPageIndex(self):
			## 0 or 1
			return self.inventoryPageIndex
	
	if app.ENABLE_GROWTH_PET_SYSTEM:	
		def __IsPetItem(self, srcItemVID):
			item.SelectItem(srcItemVID)
			
			if item.GetItemType() == item.ITEM_TYPE_PET:
				return True
			
			return False
		
	if app.ENABLE_GROWTH_PET_SYSTEM:	
		def __SendUsePetItemToItemPacket(self, srcItemVID, srcItemSlotPos, dstItemSlotPos):				
			if self.__CanUseSrcPetItemToDstPetItem(srcItemVID, srcItemSlotPos, dstItemSlotPos):
				srcItemVnum		= playerm2g2.GetItemIndex(srcItemSlotPos)
				item.SelectItem( srcItemVnum )
				srcItemType		= item.GetItemType()
				srcItemSubType	= item.GetItemSubType()
				
				if item.ITEM_TYPE_PET == srcItemType:					
					if srcItemSubType in [item.PET_FEEDSTUFF, item.PET_BAG]:
						self.__OpenPetItemQuestionDialog(srcItemSlotPos, dstItemSlotPos)
					elif item.PET_NAME_CHANGE == srcItemSubType:
						self.__UseItemPetNameChange(srcItemSlotPos, dstItemSlotPos)
				return True
				
			return False
			
		def __UseItemPetNameChange(self, srcSlotPos, dstSlotPos):
			if self.petNameChangeWindow:
				self.petNameChangeWindow.NameChangeWindowOpen( playerm2g2.INVENTORY, srcSlotPos, playerm2g2.INVENTORY, dstSlotPos )	
				
	if app.ENABLE_GROWTH_PET_SYSTEM:	
		def __IsUsablePetItem(self, srcItemVNum):
		
			item.SelectItem(srcItemVNum)
			srcItemType		= item.GetItemType()
			srcItemSubType	= item.GetItemSubType()
			
			if srcItemType != item.ITEM_TYPE_PET:
				return False
			
			if srcItemSubType not in [item.PET_FEEDSTUFF, item.PET_BAG, item.PET_NAME_CHANGE]:
				return False
			
			return True
		
	if app.ENABLE_GROWTH_PET_SYSTEM:
		def __CanUseSrcPetItemToDstPetItem(self, srcItemVNum, srcSlotPos, dstSlotPos):
			item.SelectItem(srcItemVNum)
			srcItemType		= item.GetItemType()
			srcItemSubType	= item.GetItemSubType()
			
			if srcItemType != item.ITEM_TYPE_PET:
				return False
			
			if srcItemSubType == item.PET_FEEDSTUFF:		
				detIndex = playerm2g2.GetItemIndex(dstSlotPos)
				item.SelectItem(detIndex)
				
				dstItemType		= item.GetItemType()
				dstItemSubType	= item.GetItemSubType()
				
				if dstItemType != item.ITEM_TYPE_PET:
					return False
					
				if dstItemSubType not in [item.PET_UPBRINGING]:
					return False
					
				if dstItemSubType == item.PET_BAG:
					incaseTime = playerm2g2.GetItemMetinSocket(playerm2g2.INVENTORY, dstSlotPos, 1)
					if incaseTime == 0:
						return False
			
			elif srcItemSubType == item.PET_BAG:
				
				if playerm2g2.GetItemSealDate(playerm2g2.INVENTORY, dstSlotPos) != item.E_SEAL_DATE_DEFAULT_TIMESTAMP:
					return False
			
				detIndex = playerm2g2.GetItemIndex(dstSlotPos)
				item.SelectItem(detIndex)
				
				dstItemType		= item.GetItemType()
				dstItemSubType	= item.GetItemSubType()
				
				if dstItemType != item.ITEM_TYPE_PET:
					return False
					
				if dstItemSubType not in [item.PET_UPBRINGING, item.PET_BAG]:
					return False
			
				lifeTime = playerm2g2.GetItemMetinSocket(playerm2g2.INVENTORY, dstSlotPos, 0)
					
				if dstItemSubType == item.PET_UPBRINGING:
					## 가방 아이템을 기간이 지난 육성펫에 사용불가
					if lifeTime < app.GetGlobalTimeStamp():
						return False
						
					## 가방 아이템에 이미 들어있는 상태에서는 육성펫에 사용불가
					srcIncase = playerm2g2.GetItemMetinSocket(playerm2g2.INVENTORY, srcSlotPos, 1)
					if srcIncase != 0:
						return False
						
				elif dstItemSubType == item.PET_BAG:
					## 가방 아이템을 가방에 사용할때는 dest가방의 기간이 다 지나야 한다.
					if lifeTime > app.GetGlobalTimeStamp():
						return False
						
					## 사용하려는 가방은 비어 있어야 한다.
					srcIncase = playerm2g2.GetItemMetinSocket(playerm2g2.INVENTORY, srcSlotPos, 1)
					if srcIncase != 0:
						return False
					
					## 대상 가방은 비어있으면 안된다.
					destIncase = playerm2g2.GetItemMetinSocket(playerm2g2.INVENTORY, dstSlotPos, 1)
					if destIncase == 0:
						return False
						
			elif srcItemSubType == item.PET_NAME_CHANGE:
				detIndex = playerm2g2.GetItemIndex(dstSlotPos)
				item.SelectItem(detIndex)
				
				dstItemType		= item.GetItemType()
				dstItemSubType	= item.GetItemSubType()
				
				if dstItemType != item.ITEM_TYPE_PET:
					return False
					
				if dstItemSubType not in [item.PET_UPBRINGING]:
					return False
					
			else:
				return False
			
			return True
			
	if app.ENABLE_GROWTH_PET_SYSTEM:
		def __CanUseGrowthPet(self, slotIndex):
		
			if not playerm2g2.GetItemMetinSocket(playerm2g2.INVENTORY, slotIndex, 2):
				return False
				
			(limitType, limitValue) = item.GetLimit(0)
			remain_time = 999
			if item.LIMIT_REAL_TIME == limitType:
				sock_time   = playerm2g2.GetItemMetinSocket(playerm2g2.INVENTORY, slotIndex, 0)
				if app.GetGlobalTimeStamp() > sock_time:
					chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.PET_CAN_NOT_SUMMON_BECAUSE_LIFE_TIME_END)
					return False
					
			return True
	
	if app.ENABLE_GROWTH_PET_SYSTEM:
		def __CanUsePetBagItem(self, slotIndex):
			
			if not playerm2g2.GetItemMetinSocket(playerm2g2.INVENTORY, slotIndex, 2):
				return False
				
			(limitType, limitValue) = item.GetLimit(0)
			remain_time = 999
			if item.LIMIT_REAL_TIME_START_FIRST_USE == limitType:
				sock_time   = playerm2g2.GetItemMetinSocket(playerm2g2.INVENTORY, slotIndex, 0)
				use_cnt	    = playerm2g2.GetItemMetinSocket(playerm2g2.INVENTORY, slotIndex, 1)
				
				if use_cnt:
					if app.GetGlobalTimeStamp() > sock_time:
						chatm2g.AppendChat(chatm2g.CHAT_TYPE_INFO, localeInfo.PET_CAN_NOT_USE_BAG)
						return False;
						
			return True
			
	if app.ENABLE_GROWTH_PET_SYSTEM:
		def __CanAttachGrowthPetItem(self, itemVNum, itemSlotIndex):
		
			activePetId = playerm2g2.GetActivePetItemId()
			if activePetId == 0:
				return True
			
			item.SelectItem(itemVNum)
			itemType	= item.GetItemType()
			itemSubType = item.GetItemSubType()
			
			if item.ITEM_TYPE_PET == itemType and itemSubType == item.PET_UPBRINGING:
				petId = playerm2g2.GetItemMetinSocket(itemSlotIndex, 2)
				if petId == activePetId:
					return False
					
					
			return True
			
	if app.ENABLE_GROWTH_PET_SYSTEM:
		def SetPetHatchingWindow(self, window):
			self.petHatchingWindow = window
		def SetPetNameChangeWindow(self, window):
			self.petNameChangeWindow = window
			
	if app.ENABLE_GROWTH_PET_SYSTEM:
		def SetPetFeedWindow(self, window):
			self.petFeedWindow = window
			
	if app.ENABLE_GROWTH_PET_SYSTEM:
		def ItemMoveFeedWindow(self, slotWindow, slotIndex):
			
			if not self.petFeedWindow:
				return
				
			self.petFeedWindow.ItemMoveFeedWindow(slotWindow, slotIndex)
			
	if app.ENABLE_CHEQUE_SYSTEM:
		def OverInToolTip(self, arg) :	
			arglen = len(str(arg))
			pos_x, pos_y = wndMgr.GetMousePosition()
			
			self.toolTip.ClearToolTip()
			self.toolTip.SetThinBoardSize(11 * arglen)
			self.toolTip.SetToolTipPosition(pos_x + 5, pos_y - 5)
			self.toolTip.AppendTextLine(arg, 0xffffff00)
			self.toolTip.Show()
		
		def OverOutToolTip(self) :
			self.toolTip.Hide()
		
		def EventProgress(self, event_type, idx) :
			if "mouse_over_in" == str(event_type) :
				if idx == 0 :
					self.OverInToolTip(localeInfo.CHEQUE_SYSTEM_UNIT_YANG)
				elif idx == 1 :
					self.OverInToolTip(localeInfo.CHEQUE_SYSTEM_UNIT_WON)
				else:
					return 
			elif "mouse_over_out" == str(event_type) :
				self.OverOutToolTip()
			else:
				return			