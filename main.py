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

    from taurus.core.taurusmanager import TaurusManager

    taurusM = TaurusManager()
    taurusM.changeDefaultPollingPeriod(200)  # ms

    app = TaurusApplication()

    # Add a date-time X axis
    axis = DateAxisItem(orientation="bottom")
    axis.tickValues(0,30,3)
    #ticks = [list(zip((0, 1, 2, 3, 4), (0, 1, 2, 3, 4)))]
    #axis.setTicks(ticks)



    w = pg.PlotWidget()
    w.setWindowTitle('window_name')
    axis.attachToPlotItem(w.getPlotItem())
    as1=w.getPlotItem()
    #axis.setAxisScale(self.xBottom, 0, 5 * 60)
    #axis.setXDynScale(True)

    # Add the auto-pan ("oscilloscope mode") tool
    autopan = XAutoPanTool()
    autopan.attachToPlotItem(w.getPlotItem())

    # Add Forced-read tool
    #fr = ForcedReadTool(w, period=7600)
    #fr.attachToPlotItem(w.getPlotItem())

    # add legend the legend tool
    w.addLegend()

    # adding a taurus data item...
    c2 = TaurusTrendSet(name="foo")
    c2.setModel("eval:{tango/test/1/double_scalar}")
    c2.setBufferSize(1000)
    #w.setTitleText("asfasfas")
    w.addItem(c2)

    c3 = TaurusTrendSet(name="foo3")
    c3.setModel("eval:{tango/test/1/double_scalar}*2")
    w.addItem(c3)

    #ticks = [list(zip((0, 1, 2, 3, 4), (0,1,2,3,4)))]
    #ticks = [0,1,2,3]
    #xax = w.getAxis("bottom")
    #axis.setTicks(ticks)




    w.show()

    sys.exit(app.exec_())
