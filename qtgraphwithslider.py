#!/usr/bin/env python
import sys
from taurus.qt.qtgui.application import TaurusApplication
from taurus_pyqtgraph import (
    TaurusTrendSet,
    DateAxisItem,
    XAutoPanTool,
    ForcedReadTool,
)
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import time, numpy
from taurus.core.taurusmanager import TaurusManager
from PyQt5.QtWidgets import *
import json
from tango import AttributeProxy

with open("data_file.json", "r") as read_file:
    MainDict = json.load(read_file)




class TimeGraphWithSlider(QMainWindow):
    def __init__(self,MainDict=MainDict):
        print(1)
        super(TimeGraphWithSlider,self).__init__()
        # init
        self.now0 = time.time()
        self.prev = 0
        self.T0 = 0
        self.dT = 60
        pg.setConfigOption('background', '719EB7')  ##138da5 #17a7c7
        pg.setConfigOption('foreground', 'k')
        pg.mkPen(0.5)
        taurusM = TaurusManager()
        taurusM.changeDefaultPollingPeriod(200)  # ms


        self.setWindowTitle(MainDict["window_name"])  # Название
        self.setGeometry(0, 690, 920, 350)

        # slider1
        self.slider = QSlider(QtCore.Qt.Horizontal, self)
        self.slider.resize(800, 20)
        self.slider.move(100, 330)
        self.slider.setMinimum(0)
        self.slider.setMaximum(10000)
        self.slider.setValue(10000)
        self.slider.valueChanged.connect(self.sl_move)

        # slider2
        self.slider2 = QSlider(QtCore.Qt.Vertical, self)
        self.slider2.resize(20, 300)
        self.slider2.move(900, 10)
        self.slider2.setMinimum(0)
        self.slider2.setMaximum(8)
        self.slider2.setValue(3)
        self.slider2.valueChanged.connect(self.cycle2)

        # Ось Х
        self.axis = DateAxisItem(orientation="bottom")
        self.axis.setStyle(tickFont=QtGui.QFont('Roman times', 10, QtGui.QFont.Bold))
        self.axis.setLabel("Time")

        # Добавляем треки в окно
        w = pg.PlotWidget(self)
        self.graph = w
        self.graph.resize(900, 330)
        self.axis.attachToPlotItem(w.getPlotItem())
        # Add the auto-pan ("oscilloscope mode") tool
        autopan = XAutoPanTool()
        autopan.attachToPlotItem(w.getPlotItem())
        # Add Forced-read tool
        fr = ForcedReadTool(w, period=MainDict["ForcedReadTool"])
        fr.attachToPlotItem(w.getPlotItem())

        # создаём легенду
        penleg = pg.mkPen(width=2, color='w')
        leg = w.addLegend(labelTextSize='14pt', pen=penleg, brush='w')

        # adding a taurus data item...
        for model in MainDict["Models"]:
            pen3 = pg.mkPen(width=float(model["width"]),
                            color=model["color"])  # style=QtCore.Qt.DashLine,
            c3 = TaurusTrendSet(name=model["name"], pen=pen3)  # symbolBrush=0.5,
            for s in model["model"].split(";"):
                if s.count("{") == 1:
                    if ".magnitude" in s:
                        if "=" in s:
                            s1 = s.split("{")[1].split("}")[0]
                            att = AttributeProxy(s1)
                            D_U = att.get_property('display_unit')['display_unit']
                            if str(type(D_U)) == "<class 'tango._tango.StdStringVector'>":
                                D_U = 1.0
                            else:
                                D_U = float(D_U)
                            print(D_U)
            c3.setModel(model["model"])
            w.addItem(c3)

        # стандартный таймер - функция cycle будет вызыватся каждую 1 секунд
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.cycle)
        self.timer.start(1000)

        # Ось У
        w.setRange(yRange=(MainDict["Y_axis"][0], MainDict["Y_axis"][
            1]))  # xRange=(0, 3600),                                           #ОСЬ у ПРЕДЕЛЫ
        w.getAxis('left').setPen(color=(255, 255, 255, 255), width=0.8)
        # w.getAxis('bottom').setTickSpacing(major=3600, minor = 600)
        # w.getAxis('left').setTickSpacing(major=50, minor=10)
        w.getAxis('left').setStyle(tickFont=QtGui.QFont('Roman times', 10, QtGui.QFont.Bold))
        w.setLogMode(False, MainDict["Y_axis"][2] == "log")

        w.showGrid(True, True)

    def cycle2(self):

        T = {0: 10, 1: 15, 2: 30, 3: 60, 4: 300, 5: 900, 6: 1800, 7: 3600, 8: 28800}
        self.dT = T[self.slider2.value()]
        self.prev += 1
        self.timer.setInterval(self.dT / 6 * 1000)
        self.cycle()

    def sl_move(self):
        dT=self.dT
        w = self.graph
        now = time.time()
        now0=self.now0
        if self.slider.value() != self.slider.maximum():
            self.slider.setStyleSheet("background-color:red")
            prev=self.prev
            T0=self.T0
            if True:

                self.T0 = (now - now0) / 10000 * self.slider.value() + now0

                if T0 - dT < now0:
                    w.setRange(xRange=(now0, now0 + 7 * dT / 6))
                else:
                    w.setRange(xRange=(T0 - dT, T0 + dT / 6))
        else:
            self.slider.setStyleSheet("background-color:white")
            if now - dT < now0:
                w.setRange(xRange=(now0, now0 + 7 * dT / 6))
                self.slider.hide()
            else:
                w.setRange(xRange=(now - dT, now + dT / 6))
                self.slider.show()

    def cycle(self):
        try:
            now = time.time()
            dT = self.dT
            timer = self.timer
            w = self.graph
            now0=self.now0

            # Предупреждение, если слайдер сдвига графика не в конце то делаем его красным
            if w.getAxis('bottom').range[1] > now:
                self.slider.setValue(self.slider.maximum())
            if self.slider.value() != self.slider.maximum():
                self.slider.setStyleSheet("background-color:red")
                prev=self.prev
                if self.slider.value() != prev:
                    self.prev = self.slider.value()
                    T0 = (now - now0) / 10000 * self.slider.value() + now0
                    if T0 - dT < now0:
                        w.setRange(xRange=(now0, now0 + 7 * dT / 6))
                    else:
                        w.setRange(xRange=(T0 - dT, T0 + dT / 6))
            else:
                self.slider.setStyleSheet("background-color:white")
                if w.getAxis('bottom').range[1] < now:
                    self.slider.setValue(10000 * (w.getAxis('bottom').range[0] - now0) / (now - now0))
                    print((10000 * (w.getAxis('bottom').range[0] - now0) / (now - now0)))
                else:
                    if now - dT < now0:
                        w.setRange(xRange=(now0, now0 + 7 * dT / 6))
                        self.slider.hide()
                    else:
                        w.setRange(xRange=(now - dT, now + dT / 6))
                        self.slider.show()
        except:
            pass


if __name__ == "__main__":
    print(1)

    app = TaurusApplication()


    window1=TimeGraphWithSlider(MainDict)
    window2 = TimeGraphWithSlider(MainDict)
    window1.show()
    window2.show()
    sys.exit(app.exec_())
