import sys
from taurus.external.qt import Qt
from taurus.qt.qtgui.util.ui import UILoadable
import taurus
from taurus.qt.qtgui.input import TaurusValueLineEdit, TaurusValueSpinBox, TaurusWheelEdit
import tango
import numpy
from pet10 import initpet as pet10init
import PyTango
import telegram
import time
import collections

from PyQt5 import Qt
from tango import DeviceProxy, EventType
from tango.constants import ALL_EVENTS

FREQ = 5 # Hz
# could not use all events (pytango bug!)
#QUEUE_SIZE = ALL_EVENTS
QUEUE_SIZE = 10
#b=taurus.Attribute("ET7000_server/test/pet10_7026/ao01")

bot1=telegram.Bot(token="1057965441:AAFUonNieS6Uwt-Es_XMwxVnQAO-EsSB2ag")

        
    



#from taurus.qt.qtgui.application import TaurusApplication
@UILoadable(with_ui="_ui")

class MyWidget(Qt.QTabWidget):
    
    def __init__(self, parent=None):
        
        
        Qt.QTabWidget.__init__(self, parent)
        self.loadUi(filename="Uex14.ui")
        #self._ui.pet10ao00.valueChanged.connect(self.valuechangeao00)
        #self._ui.pet10ao01.valueChanged.connect(self.valuechangeao01)
        self._ui.u2st2w.valueChanged.connect(self.valuechangeUac2st2)
        self._ui.u1st2w.valueChanged.connect(self.valuechangeUex1st2)
        self._ui.start_single_shot.clicked.connect(self.start_shot)
        self._ui.start_periodic_shot.clicked.connect(self.start_periodic)
        self._ui.stop_periodic_shot.clicked.connect(self.stop_periodic)
        #self._ui.pet10ao00.setRange(0,10*([float(i) for i in (tango.AttributeProxy("ET7000_server/test/pet10_7026/ao00").get_property("display_unit")["display_unit"])][0]))
        #self._ui.pet10ao01.setRange(0,10*([float(i) for i in (tango.AttributeProxy("ET7000_server/test/pet10_7026/ao01").get_property("display_unit")["display_unit"])][0]))
        self._ui.pet10ao01.setRange(0,100)
        #self._ui.pet10ao00.readonly(1)
        #создаём девайс прокси
        #pet10init()
        

        
        #устанавливаем частоту опросов
        #uex
        #tango_pet04.poll_attribute("ao00", 100)
        #tango_pet04.poll_attribute("ai00", 100)
        #uac
       
        #self._ui.pet10ao00label.setText(([str(i) for i in (tango.AttributeProxy("ET7000_server/test/pet10_7026/ao00").get_property("label")["label"])][0]))
        #self._ui.pet10ao01label.setText(([str(i) for i in (tango.AttributeProxy("ET7000_server/test/pet10_7026/ao01").get_property("label")["label"])][0]))
        
        #set_event_period(self, def_period) →
        #создаём атрибуты
        #uex
        #Uexatr = taurus.Attribute('ET7000_server/test/pet4_7026/ao00')
        #Uex500atr = taurus.Attribute('ET7000_server/test/pet4_7026/ai00')
        #uac
        
        #связь с элементами gui
        #Uex 
        #self._ui.Uexst.model=Uexatr 
        #self._ui.Uex500.model=Uex500atr 
        #self._ui.Uexstart.setText(Uexatr.label)
        #Uac
       
        #self._ui.Uac500.model=Uacatr# "tango:ET7000_server/test/pet10_7026/ao00" "eval:{tango:ET7000_server/test/pet10_7026/ao00}*10"
        #self._ui.Uac500.model=Uacatr
        
        #self._ui.Uac500_2.fgRole="rvalue*"+str(cc)
        #self._ui.Uac500_2.model=Uacatr #'ET7000_server/test/pet10_7026/ao00' 
        #self._ui.Uac500_2.setModelIndex('eval:b*3')
        #self._ui.Uac500_2.setFormat('{:2.1f}')
        #self._ui.Uacstart.setText(Uacatr.label)

    def valuechangeUac2st2(self):
        a=self._ui.u2st2w.value()/100*10
        bb=taurus.Attribute("pet07/ao00")
        bb.write(a)   
    def valuechangeUex1st2(self):
        a=self._ui.u1st2w.value()/100*10
        bb=taurus.Attribute("pet04/ao01")
        bb.write(a)     

    def start_shot(self):
        bb=taurus.Attribute("binp/nbi/timing/Start_single")
        bb.write(1)  
        bb=taurus.Attribute("binp/nbi/timing/Start_mode")
        bb.write(0) 
    def start_periodic(self):
        bb=taurus.Attribute("binp/nbi/timing/Start_mode")
        bb.write(1) 
    def stop_periodic(self):
        bb=taurus.Attribute("binp/nbi/timing/Start_mode")
        bb.write(0) 
   
        
  

      
from taurus.qt.qtgui.application import TaurusApplication

app = TaurusApplication(sys.argv, cmd_line_parser=None,)
panel = Qt.QTabWidget()
layout = Qt.QHBoxLayout()
panel.setLayout(layout)
w = MyWidget()
layout.addWidget(w)



#tango_pet10.subscribe_event("ao00", EventType.PERIODIC_EVENT, handle_events1)
flag=0
def vacuum_Torr(c):
    #e=tango.AttributeProxy("ET7000_server/test/pet10_7026/ao00")
    global flag    
    text = pow(10,(1.667*c.attr_value.value-11.46))*1000

    #b.write(e.attr_value.value)
    a=float(text)
    w._ui.vac_torr.setValue(a)
    w._ui.vac_torr_2.setValue(a)
    w._ui.vac_torr_3.setValue(a)
    global flag
    if ((a>1)and(flag==0)):
        bot1.sendMessage(chat_id=450820059, text = "vacuum %3.4f mTorr"%a)
        flag=1
    else:
        #bot1.sendMessage(chat_id=450820059, text = "vacuum %3.4f mTorr"%a)
        if (a<1):
            if (flag==1):
                bot1.sendMessage(chat_id=450820059, text = "вакуум улучшился!")
                flag=0
            else:
                flag=0
        else:
            flag=1

tango_pet7 = tango.DeviceProxy("pet07")
try:
    tango_pet7.subscribe_event("ai05", EventType.PERIODIC_EVENT, vacuum_Torr)
except tango.DevFailed:
    print("pet07 offline")

def uac2_str(c):
    #e=tango.AttributeProxy("ET7000_server/test/pet10_7026/ao00")
        
    text = c.attr_value.value*570/4.46

    #b.write(e.attr_value.value)
    a=float(text)
    w._ui.u2acme.setValue(a)
tango_pet9 = tango.DeviceProxy("pet09")
try:
    tango_pet9.subscribe_event("ai00", EventType.PERIODIC_EVENT, uac2_str)
except tango.DevFailed:
    print("pet09 offline")



#d=taurus.Attribute("pet10/ao00")
#d2=taurus.Attribute("pet10/ao01")
#def uprint(c):
#    print(d.rvalue," ",d2.rvalue)
#tango_pet10 = tango.DeviceProxy("pet10")
#try:
#    tango_pet10.subscribe_event("ao00", EventType.PERIODIC_EVENT, uprint)
#except tango.DevFailed:
#    print("pet10 offline")



def uex2_str(c):
    #e=tango.AttributeProxy("ET7000_server/test/pet10_7026/ao00")
        
    text = c.attr_value.value*550/4.6
    
    #b.write(e.attr_value.value)
    a=float(text)
    w._ui.u1exme.setValue(a)

tango_pet4 = tango.DeviceProxy("pet04")
try:
    tango_pet4.subscribe_event("ai00", EventType.PERIODIC_EVENT, uex2_str)
except tango.DevFailed:
    print("pet04 offline")

w._ui.vacstatus_1.model="eval:{pet05/di00}*{pet05/di01}*{pet05/di02}*{pet05/di03}*{pet05/di04}*{pet06/di00}"   
w._ui.vacstatus_2.model="eval:{pet05/di00}*{pet05/di01}*{pet05/di02}*{pet05/di03}*{pet05/di04}*{pet06/di00}"    
#w._ui.trend1.setXIsTime(True)
#w._ui.trend1.setmodel("pet10/ao00")
flag1=0
def cryo_alarm(c):
    #e=tango.AttributeProxy("ET7000_server/test/pet10_7026/ao00")
    global flag1    
    text = c.attr_name
    #print(text)
    ctrig=float(c.attr_value.value)
    #print (ctrig)

    if ((ctrig==0)and(flag1==0)):
        bot1.sendMessage(chat_id=450820059, text = "%s is off"%text)
        flag1=1
    else:
        #bot1.sendMessage(chat_id=450820059, text = "vacuum %3.4f mTorr"%a)
        if (ctrig==1):
            if (flag1==1):
                #bot1.sendMessage(chat_id=450820059, text = "вакуум улучшился!")
                flag1=0
            else:
                flag1=0
        else:
            flag1=1
    #b.write(e.attr_value.value)
    #a=float(text)
    #w._ui.u1exme.setValue(a)

tango_pet8 = tango.DeviceProxy("pet08")
channels=["di00","di01", "di02", "di03"]
for channel in channels:
    try:
        tango_pet8.subscribe_event(channel, EventType.PERIODIC_EVENT, cryo_alarm)
    except tango.DevFailed:
        print("pet08 offline")

panel.show()
sys.exit(app.exec_())