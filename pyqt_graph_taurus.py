#!/usr/bin/env python
def cycle2():
    global dT,prev,timer
    T={0:10, 1:15, 2:30,3:60,4:300,5:900,6:1800,7:3600, 8:28800}
    dT=T[Window.slider2.value()]
    prev+=1
    timer.setInterval(dT / 6 * 1000)
    cycle()
def sl_move():
    global dT, timer, w
    now = time.time()
    if Window.slider.value() != Window.slider.maximum():
        Window.slider.setStyleSheet("background-color:red")
        global prev, T0
        if True:

            T0 = (now - now0) / 10000 * Window.slider.value() + now0

            if T0 - dT < now0:
                w.setRange(xRange=(now0, now0 + 7 * dT / 6))
            else:
                w.setRange(xRange=(T0 - dT, T0 + dT / 6))
    else:
        Window.slider.setStyleSheet("background-color:white")
        if now - dT < now0:
            w.setRange(xRange=(now0, now0 + 7 * dT / 6))
            Window.slider.hide()
        else:
            w.setRange(xRange=(now - dT, now + dT / 6))
            Window.slider.show()
def cycle():
    try:
        now = time.time()
        global dT, timer, w
        # Предупреждение, если слайдер сдвига графика не в конце то делаем его красным
        if w.getAxis('bottom').range[1] > now:
            Window.slider.setValue(Window.slider.maximum())
        if Window.slider.value() != Window.slider.maximum():
            Window.slider.setStyleSheet("background-color:red")
            global prev, T0
            if Window.slider.value() != prev:
                prev = Window.slider.value()
                T0 = (now - now0) / 10000 * Window.slider.value() + now0
                if T0-dT<now0:
                    w.setRange(xRange=(now0, now0 + 7 * dT / 6))
                else:
                    w.setRange(xRange=(T0 - dT, T0 + dT / 6))
        else:
            Window.slider.setStyleSheet("background-color:white")
            if w.getAxis('bottom').range[1] <now:
                Window.slider.setValue(10000*(w.getAxis('bottom').range[0]-now0)/(now-now0))
                print((10000*(w.getAxis('bottom').range[0]-now0)/(now-now0)))
            else:
                if now - dT < now0:
                    w.setRange(xRange=(now0, now0 + 7 * dT / 6))
                    Window.slider.hide()
                else:
                    w.setRange(xRange=(now - dT, now + dT / 6))
                    Window.slider.show()
    except:
        pass


if __name__ == "__main__":
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




    #init
    now0 = time.time()
    prev = 0
    T0=0
    dT=60
    pg.setConfigOption('background', '719EB7') ##138da5 #17a7c7
    pg.setConfigOption('foreground', 'k')
    pg.mkPen(0.5)
    taurusM = TaurusManager()
    taurusM.changeDefaultPollingPeriod(200)  # ms
    app = TaurusApplication()

    #создаём окно программы
    Window=QMainWindow()
    Window.setWindowTitle(MainDict["window_name"])                                                  #Название
    Window.setGeometry(0,690,920,350)


    #slider1
    Window.slider = QSlider(QtCore.Qt.Horizontal, Window)
    Window.slider.resize(800, 20)
    Window.slider.move(100, 330)
    Window.slider.setMinimum(0)
    Window.slider.setMaximum(10000)
    Window.slider.setValue(10000)
    Window.slider.valueChanged.connect(sl_move)

    #slider2
    Window.slider2 = QSlider(QtCore.Qt.Vertical, Window)
    Window.slider2.resize(20, 300)
    Window.slider2.move(900, 10)
    Window.slider2.setMinimum(0)
    Window.slider2.setMaximum(8)
    Window.slider2.setValue(3)
    Window.slider2.valueChanged.connect(cycle2)



    # Ось Х
    axis = DateAxisItem(orientation="bottom")
    axis.setStyle(tickFont=QtGui.QFont('Roman times', 10, QtGui.QFont.Bold))
    axis.setLabel("Time")

    # Добавляем треки в окно
    w = pg.PlotWidget(Window)
    Window.graph=w
    Window.graph.resize(900, 330)
    axis.attachToPlotItem(w.getPlotItem())
    # Add the auto-pan ("oscilloscope mode") tool
    autopan = XAutoPanTool()
    autopan.attachToPlotItem(w.getPlotItem())
    # Add Forced-read tool
    fr = ForcedReadTool(w, period=MainDict["ForcedReadTool"])
    fr.attachToPlotItem(w.getPlotItem())

    # создаём легенду
    penleg=pg.mkPen(width=2,color='w')
    leg=w.addLegend(labelTextSize='14pt', pen=penleg, brush='w')

    # adding a taurus data item...
    for model in MainDict["Models"]:
        pen3 = pg.mkPen(width=float(model["width"]),
                        color=model["color"])  # style=QtCore.Qt.DashLine,
        c3 = TaurusTrendSet(name=model["name"], pen=pen3)  # symbolBrush=0.5,
        for s in model["model"].split(";"):
            if s.count("{")  ==1:
                if ".magnitude" in s:
                    if "=" in s:
                        s1=s.split("{")[1].split("}")[0]
                        att = AttributeProxy(s1)
                        D_U= att.get_property('display_unit')['display_unit']
                        if str(type(D_U)) == "<class 'tango._tango.StdStringVector'>":
                            D_U=1.0
                        else:
                            D_U=float(D_U)
                        print(D_U)
        c3.setModel(model["model"])
        w.addItem(c3)



    # стандартный таймер - функция cycle будет вызыватся каждую 1 секунд
    timer = QtCore.QTimer()
    timer.timeout.connect(cycle)
    timer.start(1000)

    #Ось У
    w.setRange(yRange=(MainDict["Y_axis"][0], MainDict["Y_axis"][1])) #xRange=(0, 3600),                                           #ОСЬ у ПРЕДЕЛЫ
    w.getAxis('left').setPen(color=(255, 255, 255, 255), width=0.8)
    #w.getAxis('bottom').setTickSpacing(major=3600, minor = 600)
    #w.getAxis('left').setTickSpacing(major=50, minor=10)
    w.getAxis('left').setStyle(tickFont=QtGui.QFont('Roman times', 10, QtGui.QFont.Bold))
    w.setLogMode(False, MainDict["Y_axis"][2] == "log")

    w.showGrid(True, True)

    w.show()
    Window.show()
    sys.exit(app.exec_())
