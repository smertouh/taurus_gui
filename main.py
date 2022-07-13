#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################


"""Example on using a tpg.TaurusTrendSet and some related tools
on a pure pyqtgraph plot"""


def cycle2():
    global dT,prev,timer
    T={0:10, 1:15, 2:30,3:60,4:300,5:900,6:1800,7:3600, 8:28800}
    dT=T[Window.slider2.value()]
    prev+=1
    timer.setInterval(dT / 6 * 1000)
    cycle()
    print (dT)


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
            # Window.slider.setEnabled(False)
            Window.slider.hide()
        else:
            w.setRange(xRange=(now - dT, now + dT / 6))
            # Window.slider.setEnabled(True)
            Window.slider.show()
def cycle():
    try:
        now = time.time()
        global dT, timer
        timer.setInterval(dT/6*1000)
        # ticks = [list(zip(timestamps, timestampsstr))]
        # ticks = [0,1,2,3]
        # xax = w.getAxis("bottom")
        # axis.setTicks(ticks)
        global w
        # print(Window.slider.value()," ",Window.slider.maximum() )
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

            """
            sl_val=max(10000 * (w.getAxis('bottom').range[0] - now0) / (now - now0),10000*dT/(now-now0))
            if sl_val==0:
                sleep(1)
                now = time.time()
                sl_val = max(10000 * (w.getAxis('bottom').range[0] - now0) / (now - now0), 0)
            if w.getAxis('bottom').range[1]>now0+7 * dT / 6:
                Window.slider.setValue(sl_val)
            print(sl_val)
            """



        else:
            Window.slider.setStyleSheet("background-color:white")

            if w.getAxis('bottom').range[1] <now:
                Window.slider.setValue(10000*(w.getAxis('bottom').range[0]-now0)/(now-now0))
                print((10000*(w.getAxis('bottom').range[0]-now0)/(now-now0)))
                #w.setRange(xRange=(w.getAxis('bottom').range[0], w.getAxis('bottom').range[1]))


            else:

                if now - dT < now0:
                    w.setRange(xRange=(now0, now0 + 7 * dT / 6))
                    # Window.slider.setEnabled(False)
                    Window.slider.hide()
                else:
                    w.setRange(xRange=(now - dT, now + dT / 6))
                    # Window.slider.setEnabled(True)
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
    Window=QMainWindow()
    Window.setWindowTitle("ICP DAS Measurements")
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



    # Add a date-time X axis
    axis = DateAxisItem(orientation="bottom")

    #ticks = [list(zip((0, 1, 2, 3, 4), (0, 1, 2, 3, 4)))]
    #axis.setTicks(ticks)



    w = pg.PlotWidget(Window)
    #w.move(0,10)
    Window.graph=w#pg.GraphicsLayoutWidget(Window)
    #Window.plt = Window.graph.addWidget(w)

    Window.graph.resize(900, 330)
    #w.setWindowTitle('vacuum trend')
    axis.attachToPlotItem(w.getPlotItem())
    #as1=w.getPlotItem()
    #axis.setAxisScale(self.xBottom, 0, 5 * 60)
    #axis.setXDynScale(True)

    # Add the auto-pan ("oscilloscope mode") tool
    autopan = XAutoPanTool()
    autopan.attachToPlotItem(w.getPlotItem())

    # Add Forced-read tool
    fr = ForcedReadTool(w, period=1000)
    fr.attachToPlotItem(w.getPlotItem())

    # add legend the legend tool
    penleg=pg.mkPen(width=2,color='w')
    #leg.labelTextColor(penleg)
    leg=w.addLegend(labelTextSize='14pt', pen=penleg, brush='w')

    # adding a taurus data item...
    pen2 = pg.mkPen(width=4, color='r')
    c2 = TaurusTrendSet(name="temperature", pen=pen2)
    c2.setModel("eval:{tango/test/1/double_scalar}")
    #c2.setBufferSize(1000)
    #w.setTitleText("asfasfas")
    w.addItem(c2)
    pen3=pg.mkPen(width=2, color='y') #style=QtCore.Qt.DashLine,
    c3 = TaurusTrendSet(name="vacuum", pen=pen3) #symbolBrush=0.5,
    #c3.setModel("eval: a=10;b={tango/test/1/double_scalar};(a*b)")
    c3.setModel("eval:a=10;b={tango/test/1/double_scalar}*1.667-11.46;a**((b+250)/500)")
    w.addItem(c3)

    # стандартный таймер - функция cycle будет вызыватся каждую 10 секунд
    timer = QtCore.QTimer()
    timer.timeout.connect(cycle)
    timer.start(1000)


    ticks = [0,3]

    w.setRange(yRange=(-250, 250)) #xRange=(0, 3600),
    w.getAxis('left').setPen(color=(255, 255, 255, 255), width=0.8)
    w.getAxis('bottom').setStyle(tickFont=QtGui.QFont('Roman times', 10, QtGui.QFont.Bold))
    w.getAxis('bottom').setLabel("Time")

    #w.getAxis('bottom').setTickSpacing(major=3600, minor = 600)

    w.getAxis('left').setTickSpacing(major=50, minor=10)
    w.getAxis('left').setStyle(tickFont=QtGui.QFont('Roman times', 10, QtGui.QFont.Bold))
    #w.setLogMode(False,True)


    now = time.time()
    w.setRange(xRange=(now - 60, now + 10))
    w.showGrid(True, True)

    w.show()
    Window.show()
    sys.exit(app.exec_())
