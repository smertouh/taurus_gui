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
from PyQt5.QtCore import QSize, QPoint
import glob, os
import pyqtgraph.exporters
import socket
import datetime


def prepare_settings(obj, widgets=()):
    p = obj.pos()
    s = obj.size()


    return [p,s]


class TimeGraphWithSlider(QMainWindow):
    def __init__(self,MainDict):
        self.MainDict=MainDict
        #print(1)

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
        self.resize(QSize(MainDict["position"][1][0], MainDict["position"][1][1]))
        self.move(QPoint(MainDict["position"][0][0], MainDict["position"][0][1]))


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
        try:
            self.slider2.setValue(self.MainDict["slider2value"])
        except:
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
        self.leg = w.addLegend(labelTextSize='14pt', pen=penleg, brush='w')

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
                            s2 = ''
                            for s3 in str(D_U):
                                if s3.isdigit():
                                    s2 += s3
                                elif s3 == ".":
                                    s2 += s3
                            try:
                                D_U = float(s2)
                            except:
                                D_U=1.0
                            print(D_U)

            c3.setModel(model["model"].split(".magnitude")[0]+".magnitude*"+str(D_U)+model["model"].split(".magnitude")[1])
            #c3.useArchiving()
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
        self.slider.hide()
        self.cycle2()
        #self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        #self.setWindowFlags(QtCore.Qt.WindowStaysOnBottomHint)
        #self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint|QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint)

        # checkbox
        self.CB = QCheckBox(self)
        self.CB.setText("on top")
        self.CB.setChecked(False)
        self.CB.stateChanged.connect(self.CBcheck)
        self.CB.move(0, 325)
    def CBcheck(self):
        if self.CB.isChecked():
            self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint|QtCore.Qt.WindowStaysOnTopHint)
            self.show()
        else:
            self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint)
            self.show()
    def closeEvent(self, event):

        super(TimeGraphWithSlider, self).closeEvent(event)
        self.timer.stop()
        a=(prepare_settings(self))
        b=[[a[0].x(), a[0].y()], [a[1].width(),a[1].height()]]
        self.MainDict.update({"position":b})
        self.MainDict.update({"slider2value":self.slider2.value()})
        s=self.MainDict["window_name"]+".json"
        with open(s, "w") as write_file:
            json.dump(self.MainDict, write_file, indent=4)
        now=time.time()
        self.graph.setRange(xRange=(self.now0, now))
        self.leg.hide()
        now = datetime.datetime.now()
        path="d:\\data\\trend\\"+str(socket.gethostname())+"\\"+now.strftime("%Y")+"\\"+now.strftime("%Y-%m")+"\\"+now.strftime("%Y-%m-%d")+"\\"+self.MainDict["window_name"]+"\\"
        if not os.path.exists(path):
            os.makedirs(path)
        path+=now.strftime("%Y-%m-%d_%H_%M")
        exporter = pg.exporters.ImageExporter(self.graph.plotItem)
        exporter.export(path+'.PNG')
        exporter2 = pg.exporters.CSVExporter(self.graph.plotItem)
        exporter2.export(path+'.csv')
        print("OK!")


        # Выход из программы
        #app = QApplication.instance()
        #app.quit()

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
                    #print((10000 * (w.getAxis('bottom').range[0] - now0) / (now - now0)))
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
    #print(1)
    windows=[]
    app = TaurusApplication()
    for file in glob.glob("Trend*.json", recursive=True):

        with open(file, "r") as read_file:
            MainDict1 = json.load(read_file)
            windows.append(TimeGraphWithSlider(MainDict1))
        for window in windows:
            window.show()
        #windows[0].setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    """
    with open("Trend_name.json", "r") as read_file:
        MainDict1 = json.load(read_file)
    with open("Trend_name2.json", "r") as read_file:
        MainDict2 = json.load(read_file)
    


    window1=TimeGraphWithSlider(MainDict1)
    window2 = TimeGraphWithSlider(MainDict2)
    window1.show()
    window2.show()
    """


    sys.exit(app.exec_())
