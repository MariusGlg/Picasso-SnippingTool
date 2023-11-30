import sys
import matplotlib
matplotlib.use("Qt5Agg")

import h5py
import numpy as np
import matplotlib.pyplot as plt
import yaml as _yaml
from numba import njit
import pandas as pd
import os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import pyqtgraph as pg
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMenuBar, QAction, qApp

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QFont, QColor, QPainter




import sys, os
import PyQt5.QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QMainWindow, QMenu, QGridLayout,QCheckBox, QSlider, QLineEdit, QSpinBox
from PyQt5.QtCore import Qt, QPoint


col_dbcluster = {0: "groups", 1: "convex_hull", 2: "area", 3: "mean_frame", 4: "com_x", 5: "com_y", 6: "std_frame",
                 7: "std_x", 8: "std_y", 9: "n"}
col_dbscan = ["frame", "x", "y", "photons", "sx", "sy", "bg", "lpx", "lpy", "ellipticity", "net_gradient",
                         "len", "n", "photon_rate", "group"]  # column names of dbscan file





# class PlotFigure(FigureCanvasQTAgg):
#
#     def __init__(self, parent=None, width=5, height=4, dpi=100):
#         fig, ax = plt.subplots(constrained_layout=True)
#         super(PlotFigure, self).__init__(fig)
#
#         self.canvas = pg.PlotWidget()
#         self.canvas.plotItem.setAutoVisible(y=True)
#
#         self.canvas.setWindowTitle('Scatter plot')
#         self.canvas.setAspectLocked(True)


# class Draw_Roi(QtWidgets.QMainWindow):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         #self.scene().sigMouseClicked.connect(self.mouse_clicked)
#         self.plot_widget = pg.PlotWidget()
#         self.plot_widget.scene().sigMouseClicked.connect(self.mouse_clicked)
#
#     def mouse_clicked(self, mouseClickEvent):
#         print('clicked plot 0x{:x}, event: {}'.format(id(self), mouseClickEvent))


class RoiWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROI Window")

        self.buttonlayout2 = QHBoxLayout()
        self.btn_in_ROI = QPushButton("keep Data in ROI")
        self.btn_outiside_ROI = QPushButton("keep Data outside ROI")
        self.btn_apply = QPushButton("Apply")
        self.buttonlayout2.addWidget(self.btn_in_ROI)
        self.buttonlayout2.addWidget(self.btn_outiside_ROI)
        self.buttonlayout2.addWidget(self.btn_apply)
        self.setLayout(self.buttonlayout2)

class AcceptRoi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROI")

        self.layout = QVBoxLayout()
        self.label_widget = QLabel("Accept ROI?")
        self.btn_layout = QHBoxLayout()
        self.accept_btn = QPushButton("Accept")
        self.accept_btn.setCheckable(True)

        #self.accept_btn.setEnabled(True)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setCheckable(True)
        self.btn_layout.addWidget(self.accept_btn)
        self.btn_layout.addWidget(self.clear_btn)

        self.layout.addWidget(self.label_widget)
        self.layout.addLayout(self.btn_layout)

        self.setLayout(self.layout)


class FileWindow(QWidget):
    def __init__(self, alldata, filepath_list, colorlist):
        self.alldata = alldata
        self.filepath_list = filepath_list
        self.colorlist = colorlist
        super().__init__()
        self.setWindowTitle("All files")
        self.checkboxlayout = QVBoxLayout(self)
        self.checkboxstate = 2  # clicked, activated

    def update_checkbox(self):
        checkboxlist = []
        for i in reversed(range(self.checkboxlayout.count())):
            self.checkboxlayout.itemAt(i).widget().setParent(None)
        for i in range(len(self.alldata)):
            self.checkbox = QtWidgets.QCheckBox("{}".format(str(self.filepath_list[i])))
            self.checkbox.setChecked(True)
            checkboxlist.append(self.checkbox)
            self.checkboxlayout.addWidget(self.checkbox)
            self.checkbox.stateChanged.connect(self.click)

    def click(self, state):
        if state == Qt.Checked:
            self.checkboxstate = state
        else:
            self.checkboxstate = state


class MainWindow(QWidget):  # QWidget
    def __init__(self):
        super(MainWindow, self).__init__()
        # self.resize(600, 600)
        self.setAcceptDrops(True)
        self.data_filtered = []
        self.alldata = []
        self.filepath_list = []
        self.roi_list = []

        # # Menu Bar
        # self.myQMenuBar = QtGui.QMenuBar(self)
        # exitMenu = self.myQMenuBar.addMenu('File')
        # self._createMenuBar()
        # self._createActions()
        # self._createMenuBar()
        # self._createToolBars()

        self.colorlist = ["c", "b", "k", "b", "m", "w", "r"]
        # call all subclasses

        self.initUI()
        self.w = RoiWindow()

        #self.loaded_files = FileWindow(self.alldata, self.filepath_list, self.colorlist)
        # self.plot_widget = pg.PlotWidget()
        # self.plot_widget.setBackground("w")

        # initialize AcceptRoi
        self.accept_win = AcceptRoi()

    def initUI(self):
        # Set general properties
        self.setWindowTitle("SMLM Mask")
        self.resize(800, 600)
        self.setStyleSheet("background-color: white;")

        # Create buttons
        self.plot_btn = QPushButton("plot")
        self.draw_btn = QPushButton("draw_ROI")
        self.draw_btn.setCheckable(True)
        self.create_mask_btn = QPushButton("cut")
        self.load_mask_btn = QPushButton("load_mask")
        self.create_mask_btn.setCheckable(True)
        self.save_mask_btn = QPushButton("save mask")
        self.reset_btn = QPushButton("reset")
        self.add_ROI_btn = QPushButton("add ROI")
        self.add_ROI_btn.setCheckable(True)
        self.disableBtn(self.add_ROI_btn)
        self.remove_ROI_btn = QPushButton("remove ROI")
        #self.remove_ROI_btn.setCheckable(True)

        # Create Label
        self.lbl = QLabel()
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setText('\n\n Drop .HDF5 Files \n\n')
        self.lbl.setFont(QFont("Times font", 22))
        self.lbl.setStyleSheet("background-color: lightblue; border: 2px dashed;")

        # Add GridLayout for checkboxes
        self.checkboxGroup = QGridLayout()
        self.sp = QSpinBox()
        # size of points in plot
        self.point_size = 2
        self.sp.setValue(self.point_size)
        self.sp.setRange(1,50)
        self.sp.valueChanged.connect(self.getLineEditInput)

        # Create Girdlayout and add Widgets
        self.gridLayout = QGridLayout()
        self.gridLayout.addWidget(self.lbl, 0, 0, 5, 5)

        self.gridLayout.addLayout(self.checkboxGroup, 0, 5, 5, 2)
        self.gridLayout.addWidget(self.add_ROI_btn, 3, 5, 1, 1)
        self.gridLayout.addWidget(self.remove_ROI_btn, 3, 6, 1, 1)
        self.gridLayout.addWidget(self.sp, 4, 5, 1, 1)
        self.gridLayout.addWidget(self.plot_btn, 5, 0, 1, 1)
        self.gridLayout.addWidget(self.draw_btn, 5, 1, 1, 1)
        self.gridLayout.addWidget(self.create_mask_btn, 5, 2, 1, 1)
        self.gridLayout.addWidget(self.save_mask_btn, 5, 3, 1, 1)
        self.gridLayout.addWidget(self.reset_btn, 5, 4, 1, 1)

        # Set Layout
        self.setLayout(self.gridLayout)

        # # Connect buttons to functions
        self.plot_btn.pressed.connect(self.init_Plot)
        self.draw_btn.clicked.connect(self.draw)
        #self.draw_btn.clicked.connect(self.create_mask)
        #self.create_mask_btn.pressed.connect(self.apply_mask)
        # self.load_mask_btn.pressed.connect(self.load_mask)
        # self.save_mask_btn.pressed.connect(self.save_mask)
        # self.reset_btn.pressed.connect(self.reset)
        self.add_ROI_btn.clicked.connect(self.draw)

        # # create PlotWidget
        # self.plot_widget = pg.PlotWidget()
        # self.plot_widget.setBackground("w")

    def _createActions(self):
        # Creating action using the first constructor
        self.newAction = QAction(self)
        self.newAction.setText("&New")
        # Creating actions using the second constructor
        # File
        self.openAction = QAction("&Open...", self)
        self.saveAction = QAction("&Save", self)
        self.exitAction = QAction("&Exit", self)
        # Edit
        self.copyAction = QAction("&Add_ROI", self)
        self.pasteAction = QAction("&Delete_ROI", self)
        self.cutAction = QAction("&Invert_ROI", self)
        # Help
        self.helpContentAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)

    # def _createMenuBar(self):
    #     menuBar = self.menuBar()
    #     # Creating menus using a QMenu object
    #     fileMenu = QMenu("&File", self)
    #     menuBar.addMenu(fileMenu)
    #     fileMenu.addAction(self.newAction)
    #     fileMenu.addAction(self.openAction)
    #     fileMenu.addAction(self.saveAction)
    #     fileMenu.addAction(self.exitAction)
    #
    #     # Creating menus using a title
    #     editMenu = menuBar.addMenu("&Edit")
    #     editMenu.addAction(self.copyAction)
    #     editMenu.addAction(self.pasteAction)
    #     editMenu.addAction(self.cutAction)
    #
    #     helpMenu = menuBar.addMenu("&Help")
    #     helpMenu.addAction(self.helpContentAction)
    #     helpMenu.addAction(self.aboutAction)

    # Drag and Drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):

        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            self.file_path = event.mimeData().urls()[0].toLocalFile()

            self.data = self.load()
            self.alldata.append(self.data)
            self.filepath_list.append(os.path.basename(self.file_path))
            self.show()
            event.accept()
            self.update_label_text()
            self.update_checkbox()
        else:
            event.ignore()

    def update_label_text(self):
        self.lbl.setFont(QFont("Times font", 22))
        if len(self.alldata) == 1:
            self.lbl.setText("{} file loaded".format(len(self.alldata)))  # update text
            self.setStyleSheet('''QLabel{border: 4px dashed #aaa}''')
            self.setStyleSheet("background-color: white;")
        else:
            self.lbl.setText("{} files loaded".format(len(self.alldata)))  # update text
            self.setStyleSheet('''QLabel{border: 4px dashed #aaa}''')
            self.setStyleSheet("background-color: white;")


    def update_checkbox(self):
        self.checkboxList = []
        if not self.filepath_list:
            print("zero entries")
        else:
            for i in range(len(self.filepath_list)):
                checkBox = QCheckBox('{}'.format(self.filepath_list[i]), self)
                checkBox.setChecked(True)
                self.checkboxList.append(checkBox)
                self.checkboxGroup.addWidget(checkBox, i, 0)
                self.checkboxGroup.setRowStretch(self.checkboxGroup.rowCount(), 1)
                self.checkboxGroup.setSpacing(5)
        for i in range(len(self.checkboxList)):
            self.checkboxList[i].stateChanged.connect(self.update_plot)

    def getLineEditInput(self):
        """get input from QSpinBox and updates plot"""
        self.point_size = self.sp.value()
        self.update_plot()


    def load(self):
        """load .hdf5_file"""
        with h5py.File(self.file_path, "r") as locs_file:
            key = list(locs_file.keys())[0]  # get key name
            locs = locs_file[str(key)][...]
        data_pd = pd.DataFrame(locs)
        return data_pd

    def disableBtn(self, b):
        # disable button clicks
        b.setEnabled(False)

    def enableBtn(self, b):
        b.setEnabled(True)

    def init_Plot(self):
        """Set initial plot settings"""

        # create PlotWidget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("w")

        # disable plot button
        self.disableBtn(self.plot_btn)

        # init line_plot
        self.lineplot = pg.PlotCurveItem(pen=pg.mkPen(width=3, color="k"))

        self.painter = QtGui.QPainter(self)
        self.plot_widget.addItem(self.lineplot)
        #self.plot_widget.addItem(self.painter)

        # Replace Label with PlotWidget
        self.gridLayout.replaceWidget(self.lbl, self.plot_widget)
        self.scatterPlotItemList = []

        # Loop over all data after plot_btn is pressed and generate plot_widget
        for i in range(len(self.alldata)):
            # Add some colors, loop repetitively over colorlist
            if i >= len(self.colorlist):
                i = i % len(self.colorlist)
            self.scatter = pg.ScatterPlotItem(pen=pg.mkPen(width=1, color=self.colorlist[i]),
                                              symbol='o', size=self.point_size)
            self.plot_widget.addItem(self.scatter)
            self.scatter.setData(x=self.alldata[i]["x"], y=self.alldata[i]["y"], marker="+", size=5)
            # Add to the mainlayout
            self.plot_widget.plotItem.setAutoVisible(y=True)
            self.scatterPlotItemList.append(self.scatter)


    def update_plot(self):
        '''Update plot dependend on checkbox state, size of points'''

        for i in range(len(self.alldata)):
            # Add some colors, loop repetitively over colorlist
            if i >= len(self.colorlist):
                i = i % len(self.colorlist)

            if not self.checkboxList[i].isChecked(): # + 1 -> first element is lineplot, is ignored
                self.plot_widget.listDataItems()[i+1].hide() # hide if box is unchecked
                self.scatterPlotItemList[i].setSize(self.point_size)
            else:
                self.plot_widget.listDataItems()[i+1].show() # show if box is checked
                self.scatterPlotItemList[i].setSize(self.point_size)

    def update_file_paths(self):
        pass

    def draw(self):
        self.x = []
        self.y = []
        self.xy_list = []
        if self.draw_btn.isChecked():
            self.plot_widget.scene().sigMouseClicked.connect(self.plot_ROI)

        if self.add_ROI_btn.isChecked():
            print("Add btn is checked")


    def create_mask(self):
        self.x = []
        self.y = []
        self.xy_list = []
        if self.draw_btn.isChecked():
            print("draw btn is down")

        #print(self.add_ROI_btn.isChecked())
        if self.add_ROI_btn.isDown():
            print("is down")
            self.accept_win.accept_btn.setChecked(False)  # reset accept_btn

        self.plot_widget.scene().sigMouseClicked.connect(self.plot_ROI)

    def plot_ROI(self, mouseClickEvent):
        """draws line on plot based on user defined mouseclick"""

        if self.draw_btn.isChecked() and not self.accept_win.accept_btn.isChecked():  # main switch to allow drawing in scene
            #print("is draw is checked")
            coordinates = mouseClickEvent.scenePos()
            if self.plot_widget.sceneBoundingRect().contains(coordinates):
                self.mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(coordinates)
                if mouseClickEvent.button() == 1:  # Add line if left mouse is clicked
                    self.x.append(self.mouse_point.x())
                    self.y.append(self.mouse_point.y())
                    print(self.x)
                if mouseClickEvent.button() == 2:  # remove if right mouse is clicked
                    self.x = self.x[:-1]
                    self.y = self.y[:-1]
                    self.xy_list = np.vstack((self.x, self.y))
                if mouseClickEvent.double():
                    self.x = self.x[:-1]
                    self.y = self.y[:-1]
                    self.x.append(self.x[0])  # add first x-position to close ROI
                    self.y.append(self.y[0])  # add first y-position to close ROI
                    self.xy_list.append(self.x)  # append to xy_list
                    self.xy_list.append(self.y)
                    self.lineplot.setData(x=self.x, y=self.y)
                    print(self.xy_list)

                    # after double click open new window: ask for acceptance or clearance of ROI
                    self.accept_win.show()
                    self.accept_win.accept_btn.pressed.connect(self.accept_ROI)
                    self.accept_win.clear_btn.pressed.connect(self.clear_ROI)


                self.lineplot.setData(x=self.x, y=self.y)
                self.plot_widget.plot(self.x, self.y, symbol='+', symbolSize=10)


    def accept_ROI(self):
          # Disable if ROI is completed and accepted
        #self.roi_list.append((self.xy_list))
        self.enableBtn(self.add_ROI_btn)
        if self.accept_win.accept_btn.isDown():
            self.accept_win.accept_btn.setChecked(True)
        # if accept btn is clicked -> self.roi_list.append((self.xy_list))
        if self.accept_win.accept_btn.isChecked():
            self.roi_list.append((self.xy_list))
            self.accept_win.accept_btn.setChecked(False)
            #print(self.roi_list)

        self.accept_win.close()

    def clear_ROI(self):
        print("cleared")
        self.accept_win.close()




    def apply_mask(self):
        # self.ROI_x.append(self.ROI_x[0])
        # self.ROI_y.append(self.ROI_y[0])


        for i in range(len(self.alldata)):
            # Add some colors, loop repetitively over colorlist
            if i >= len(self.colorlist):
                i = i % len(self.colorlist)

            if not self.checkboxList[i].isChecked(): # + 1 -> first element is lineplot, is ignored
                self.plot_widget.listDataItems()[i+1].hide() # hide if box is unchecked
                self.scatterPlotItemList[i].setSize(self.point_size)
            else:
                self.plot_widget.listDataItems()[i+1].show() # show if box is checked
                self.scatterPlotItemList[i].setSize(self.point_size)
                self.scatter.setData(x=self.alldata[i]["x"], y=self.alldata[i]["y"], marker='o')

        for i in range(len(self.alldata)):
            #self.plot_widget.update_plot(self.ROI_x, self.ROI_y, fillLevel=0, fillOutline=True)

            polygon = np.stack((self.ROI_x, self.ROI_y), axis=1)
            points = np.stack((self.data["x"].to_numpy(), self.data["y"].to_numpy()), axis=1)
            self.points_inside = [check_points_in_ROI(point[0], point[1], polygon) for point in points]
            # replace button interface
            #self.change_btn_layout(self.buttonlayout, self.buttonlayout_ROI)
            self.window2()

        #self.btn_in_ROI.pressed.connect(self.get_locs_inside)
        #self.btn_outiside_ROI.pressed.connect(self.get_locs_outisde)
        #self.btn_apply.pressed.connect(self.change_btn_back)


    def window2(self):
        self.w.show()
        #self.get_locs_inside()
        #self.w.btn_in_ROI.pressed.connect(self.w.locs_inside_clicked)
        self.w.btn_in_ROI.pressed.connect(self.get_locs_inside)
        self.w.btn_outiside_ROI.pressed.connect(self.get_locs_outisde)
        self.w.btn_apply.pressed.connect(self.apply_close)


    def apply_close(self):
        self.w.close()


    def get_locs_inside(self):
        self.data_filtered = self.data.loc[self.points_inside, :]
        self.scatter.setData(x=self.data_filtered["x"], y=self.data_filtered["y"])
        #self.plot_widget.setXRange(self.LEFT_X, self.RIGHT_X)
        #self.plot_widget.setYRange(self.LOW_Y, self.TOP_Y)
        for i in reversed(range(self.verticallayout.count())):
            print(self.verticallayout.itemAt(i))
        #self.change_btn_back(self.buttonlayout)
        #return self.data_filtered

    def get_locs_outisde(self):
        points_outside = [not elem for elem in self.points_inside]  # reverse to get locs out of the ROI
        self.data_filtered = self.data.loc[points_outside, :]
        self.scatter.setData(x=self.data_filtered["x"], y=self.data_filtered["y"])
        #self.plot_widget.setXRange(self.LEFT_X, self.RIGHT_X)
        #self.plot_widget.setYRange(self.LOW_Y, self.TOP_Y)
        #self.change_btn_back(self.buttonlayout)



    def load_mask(self):
        pass
    def save_mask(self):
        pass

    def reset(self):
        self.plot_data_btn.setDisabled(False)  # disable button
        self.draw_btn.setCheckable(False)
        self.horizontal_layout.replaceWidget(self.plot_widget, self.lbl)
        self.ROI_x = []
        self.ROI_y = []
        self.plot_widget.setParent(None)  # remove widget
        self.data = []
        self.lbl.setText('\n\n Drop .HDF5 File Here \n\n')



@njit(nopython=True)
def check_points_in_ROI(x, y, polygon):
    # calculates if point is inside polygon. Returns list of booleans.
    n = len(polygon)
    inside = False
    xints = 0.0
    p1x,p1y = polygon[0]
    for i in range(n+1):
        p2x,p2y = polygon[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside


app = QApplication(sys.argv)
demo = MainWindow()
demo.show()
sys.exit(app.exec_())





# if not self.data.empty:
        #     #  Set white background and black foreground
        #     pg.setConfigOption('background', 'w')
        #     pg.setConfigOption('foreground', 'k')
        #
        #     # create a PlotWidget
        #     self.plot_widget = pg.PlotWidget()
        #     # create a scatter object
        #     self.scatter = pg.ScatterPlotItem(pen=pg.mkPen(width=1, color='k'),
        #                                       symbol='o', size=5)
        #     # add scatter object to Plotwidget
        #     self.plot_widget.addItem(self.scatter)
        #     # set the data
        #     self.scatter.setData(x=self.data["x"], y=self.data["y"])
        #     # add to the mainlayout
        #     self.mainlayout.replaceWidget(self.lbl, self.plot_widget)
        #     self.plot_widget.plotItem.setAutoVisible(y=True)
        #
        #     # # get axis dimension from plot. Uses boundaries for ROI drawing
        #     # ax_x = self.plot_widget.getAxis('bottom')
        #     # #self.LEFT_X = ax_x.range[0]
        #     # self.LEFT_X = self.data["x"].loc[self.data["x"].idxmin()]
        #     # #self.RIGHT_X = ax_x.range[1]
        #     # self.RIGHT_X = self.data["x"].loc[self.data["x"].idxmax()]
        #     # ax_y = self.plot_widget.getAxis('top')
        #     # #self.LOW_Y = ax_y.range[0]
        #     # self.LOW_Y = self.data["y"].loc[self.data["y"].idxmin()]
        #     # #self.TOP_Y = ax_y.range[1]
        #     # self.TOP_Y = self.data["y"].loc[self.data["y"].idxmax()]
        #     # uses scene and sigMouseMoved to draw a user defined ROI based on mouseclicks
        #     # self.plot_widget.scene().sigMouseClicked.connect(self.mouse_clicked)
        #     # disable button
        #     self.plot_data_btn.setDisabled(True)


# if index_x > self.LEFT_X and index_x <= self.RIGHT_X and index_y > self.LOW_Y and index_y <= self.TOP_Y:
                #     if mouseClickEvent.button() == 1:  # Add line if left mouse is clicked
                #         self.ROI_x.append(mouse_point.x())
                #         self.ROI_y.append(mouse_point.y())
                #         self.lines.setData(self.ROI_x, self.ROI_y)
                #         self.points.setData(self.ROI_x, self.ROI_y)
                #     if mouseClickEvent.button() == 2:  # remove if richt mouse is clicked
                #         print("2")
                #         self.ROI_x.pop(-1)
                #         self.ROI_y.pop(-1)
                #         self.lines.setData(self.ROI_x, self.ROI_y)
                #         self.points.setData(self.ROI_x, self.ROI_y)


# def change_btn_layout(self, firstlayout, newlayout):
#     for i in reversed(range(firstlayout.count())):
#         firstlayout.itemAt(i).widget().hide()
#     self.buttonlayout.addWidget(self.btn_in_ROI)
#     self.buttonlayout.addWidget(self.btn_outiside_ROI)
#     self.buttonlayout.addWidget(self.btn_apply)
#
# def change_btn_back(self):
#     self.buttonlayout.removeWidget(self.btn_in_ROI)
#     self.buttonlayout.removeWidget(self.btn_outiside_ROI)
#     for i in reversed(range(self.buttonlayout.count())):
#         self.buttonlayout.itemAt(i).widget().show()


