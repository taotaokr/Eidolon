# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/ui/Draw2DView.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Draw2DView(object):
    def setupUi(self, Draw2DView):
        Draw2DView.setObjectName(_fromUtf8("Draw2DView"))
        Draw2DView.resize(806, 763)
        self.gridLayout = QtGui.QGridLayout(Draw2DView)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.vsplit = QtGui.QSplitter(Draw2DView)
        self.vsplit.setOrientation(QtCore.Qt.Horizontal)
        self.vsplit.setObjectName(_fromUtf8("vsplit"))
        self.hsplit = QtGui.QSplitter(self.vsplit)
        self.hsplit.setMinimumSize(QtCore.QSize(50, 0))
        self.hsplit.setOrientation(QtCore.Qt.Vertical)
        self.hsplit.setChildrenCollapsible(False)
        self.hsplit.setObjectName(_fromUtf8("hsplit"))
        self.drawWidgetTL = QtGui.QWidget(self.hsplit)
        self.drawWidgetTL.setObjectName(_fromUtf8("drawWidgetTL"))
        self.drawWidgetBL = QtGui.QWidget(self.hsplit)
        self.drawWidgetBL.setObjectName(_fromUtf8("drawWidgetBL"))
        self.verticalLayoutWidget = QtGui.QWidget(self.vsplit)
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.mainLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.mainLayout.setObjectName(_fromUtf8("mainLayout"))
        self.drawWidget = QtGui.QWidget(self.verticalLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.drawWidget.sizePolicy().hasHeightForWidth())
        self.drawWidget.setSizePolicy(sizePolicy)
        self.drawWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.drawWidget.setObjectName(_fromUtf8("drawWidget"))
        self.mainLayout.addWidget(self.drawWidget)
        self.dataGroup = QtGui.QGroupBox(self.verticalLayoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dataGroup.sizePolicy().hasHeightForWidth())
        self.dataGroup.setSizePolicy(sizePolicy)
        self.dataGroup.setObjectName(_fromUtf8("dataGroup"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.dataGroup)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_2 = QtGui.QLabel(self.dataGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(46, 0))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_3.addWidget(self.label_2)
        self.sourceBox = QtGui.QComboBox(self.dataGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sourceBox.sizePolicy().hasHeightForWidth())
        self.sourceBox.setSizePolicy(sizePolicy)
        self.sourceBox.setObjectName(_fromUtf8("sourceBox"))
        self.horizontalLayout_3.addWidget(self.sourceBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.planeLabel = QtGui.QLabel(self.dataGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.planeLabel.sizePolicy().hasHeightForWidth())
        self.planeLabel.setSizePolicy(sizePolicy)
        self.planeLabel.setMinimumSize(QtCore.QSize(46, 0))
        self.planeLabel.setObjectName(_fromUtf8("planeLabel"))
        self.horizontalLayout_4.addWidget(self.planeLabel)
        self.planeBox = QtGui.QComboBox(self.dataGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.planeBox.sizePolicy().hasHeightForWidth())
        self.planeBox.setSizePolicy(sizePolicy)
        self.planeBox.setObjectName(_fromUtf8("planeBox"))
        self.planeBox.addItem(_fromUtf8(""))
        self.planeBox.addItem(_fromUtf8(""))
        self.planeBox.addItem(_fromUtf8(""))
        self.horizontalLayout_4.addWidget(self.planeBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.sliceLabel = QtGui.QLabel(self.dataGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sliceLabel.sizePolicy().hasHeightForWidth())
        self.sliceLabel.setSizePolicy(sizePolicy)
        self.sliceLabel.setMinimumSize(QtCore.QSize(46, 0))
        self.sliceLabel.setObjectName(_fromUtf8("sliceLabel"))
        self.horizontalLayout.addWidget(self.sliceLabel)
        self.imageBox = QtGui.QSpinBox(self.dataGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageBox.sizePolicy().hasHeightForWidth())
        self.imageBox.setSizePolicy(sizePolicy)
        self.imageBox.setMaximum(999)
        self.imageBox.setObjectName(_fromUtf8("imageBox"))
        self.horizontalLayout.addWidget(self.imageBox)
        self.imageSlider = QtGui.QSlider(self.dataGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageSlider.sizePolicy().hasHeightForWidth())
        self.imageSlider.setSizePolicy(sizePolicy)
        self.imageSlider.setMaximum(10)
        self.imageSlider.setPageStep(1)
        self.imageSlider.setOrientation(QtCore.Qt.Horizontal)
        self.imageSlider.setInvertedControls(False)
        self.imageSlider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.imageSlider.setTickInterval(1)
        self.imageSlider.setObjectName(_fromUtf8("imageSlider"))
        self.horizontalLayout.addWidget(self.imageSlider)
        self.indicatorBox = QtGui.QCheckBox(self.dataGroup)
        self.indicatorBox.setChecked(True)
        self.indicatorBox.setObjectName(_fromUtf8("indicatorBox"))
        self.horizontalLayout.addWidget(self.indicatorBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.secondsButton = QtGui.QToolButton(self.dataGroup)
        self.secondsButton.setObjectName(_fromUtf8("secondsButton"))
        self.horizontalLayout_2.addWidget(self.secondsButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.label = QtGui.QLabel(self.dataGroup)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.sliceWidthBox = QtGui.QDoubleSpinBox(self.dataGroup)
        self.sliceWidthBox.setDecimals(3)
        self.sliceWidthBox.setMinimum(0.001)
        self.sliceWidthBox.setSingleStep(0.2)
        self.sliceWidthBox.setProperty("value", 0.2)
        self.sliceWidthBox.setObjectName(_fromUtf8("sliceWidthBox"))
        self.horizontalLayout_2.addWidget(self.sliceWidthBox)
        self.label_3 = QtGui.QLabel(self.dataGroup)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_2.addWidget(self.label_3)
        self.lineWidthBox = QtGui.QDoubleSpinBox(self.dataGroup)
        self.lineWidthBox.setDecimals(3)
        self.lineWidthBox.setMinimum(0.001)
        self.lineWidthBox.setSingleStep(0.2)
        self.lineWidthBox.setProperty("value", 0.2)
        self.lineWidthBox.setObjectName(_fromUtf8("lineWidthBox"))
        self.horizontalLayout_2.addWidget(self.lineWidthBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.mainLayout.addWidget(self.dataGroup)
        self.gridLayout.addWidget(self.vsplit, 0, 0, 1, 1)

        self.retranslateUi(Draw2DView)
        QtCore.QMetaObject.connectSlotsByName(Draw2DView)

    def retranslateUi(self, Draw2DView):
        Draw2DView.setWindowTitle(_translate("Draw2DView", "Form", None))
        self.dataGroup.setTitle(_translate("Draw2DView", "Data Sources", None))
        self.label_2.setText(_translate("Draw2DView", "Source", None))
        self.sourceBox.setToolTip(_translate("Draw2DView", "Select the source image to view", None))
        self.planeLabel.setText(_translate("Draw2DView", "Plane", None))
        self.planeBox.setToolTip(_translate("Draw2DView", "Select the plane at which to view the source image", None))
        self.planeBox.setItemText(0, _translate("Draw2DView", "XY", None))
        self.planeBox.setItemText(1, _translate("Draw2DView", "YZ", None))
        self.planeBox.setItemText(2, _translate("Draw2DView", "XZ", None))
        self.sliceLabel.setText(_translate("Draw2DView", "Slice", None))
        self.imageBox.setToolTip(_translate("Draw2DView", "Slice number/position being viewed", None))
        self.imageSlider.setToolTip(_translate("Draw2DView", "Set slice number/position", None))
        self.indicatorBox.setToolTip(_translate("Draw2DView", "Show the view plane indicator in the 3D view", None))
        self.indicatorBox.setText(_translate("Draw2DView", "3D Plane", None))
        self.secondsButton.setToolTip(_translate("Draw2DView", "Select secondary images/meshes to view in conjunction with source image", None))
        self.secondsButton.setText(_translate("Draw2DView", "Secondary Sources", None))
        self.label.setText(_translate("Draw2DView", "Slice Width", None))
        self.sliceWidthBox.setToolTip(_translate("Draw2DView", "Width of slices of images view at angles", None))
        self.label_3.setText(_translate("Draw2DView", "Line Width", None))
        self.lineWidthBox.setToolTip(_translate("Draw2DView", "Width of mesh lines", None))

