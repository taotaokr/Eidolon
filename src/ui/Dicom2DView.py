# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/ui/Dicom2DView.ui'
#
# Created: Fri May  5 14:57:50 2017
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_Dicom2DView(object):
    def setupUi(self, Dicom2DView):
        Dicom2DView.setObjectName(_fromUtf8("Dicom2DView"))
        Dicom2DView.resize(831, 834)
        self.gridLayout = QtGui.QGridLayout(Dicom2DView)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.drawWidget = QtGui.QWidget(Dicom2DView)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.drawWidget.sizePolicy().hasHeightForWidth())
        self.drawWidget.setSizePolicy(sizePolicy)
        self.drawWidget.setObjectName(_fromUtf8("drawWidget"))
        self.gridLayout.addWidget(self.drawWidget, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.stackGroup = QtGui.QGroupBox(Dicom2DView)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackGroup.sizePolicy().hasHeightForWidth())
        self.stackGroup.setSizePolicy(sizePolicy)
        self.stackGroup.setObjectName(_fromUtf8("stackGroup"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.stackGroup)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.seriesListWidget = QtGui.QListWidget(self.stackGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.seriesListWidget.sizePolicy().hasHeightForWidth())
        self.seriesListWidget.setSizePolicy(sizePolicy)
        self.seriesListWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.seriesListWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.seriesListWidget.setDragEnabled(True)
        self.seriesListWidget.setDragDropOverwriteMode(True)
        self.seriesListWidget.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.seriesListWidget.setObjectName(_fromUtf8("seriesListWidget"))
        self.horizontalLayout_3.addWidget(self.seriesListWidget)
        self.horizontalLayout.addWidget(self.stackGroup)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(Dicom2DView)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(330, 0))
        self.groupBox.setMaximumSize(QtCore.QSize(330, 16777215))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.imgNumBox = QtGui.QSpinBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imgNumBox.sizePolicy().hasHeightForWidth())
        self.imgNumBox.setSizePolicy(sizePolicy)
        self.imgNumBox.setMaximum(9999)
        self.imgNumBox.setObjectName(_fromUtf8("imgNumBox"))
        self.horizontalLayout_6.addWidget(self.imgNumBox)
        self.imgSlider = QtGui.QSlider(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imgSlider.sizePolicy().hasHeightForWidth())
        self.imgSlider.setSizePolicy(sizePolicy)
        self.imgSlider.setMinimumSize(QtCore.QSize(230, 0))
        self.imgSlider.setOrientation(QtCore.Qt.Horizontal)
        self.imgSlider.setObjectName(_fromUtf8("imgSlider"))
        self.horizontalLayout_6.addWidget(self.imgSlider)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(Dicom2DView)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setMinimumSize(QtCore.QSize(330, 0))
        self.groupBox_2.setMaximumSize(QtCore.QSize(330, 16777215))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_2.addWidget(self.label_3)
        self.imgStartBox = QtGui.QSpinBox(self.groupBox_2)
        self.imgStartBox.setMaximum(9999)
        self.imgStartBox.setSingleStep(5)
        self.imgStartBox.setObjectName(_fromUtf8("imgStartBox"))
        self.horizontalLayout_2.addWidget(self.imgStartBox)
        self.setStartButton = QtGui.QPushButton(self.groupBox_2)
        self.setStartButton.setMaximumSize(QtCore.QSize(65, 16777215))
        self.setStartButton.setObjectName(_fromUtf8("setStartButton"))
        self.horizontalLayout_2.addWidget(self.setStartButton)
        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_2.addWidget(self.label_4)
        self.imgEndBox = QtGui.QSpinBox(self.groupBox_2)
        self.imgEndBox.setMaximum(9999)
        self.imgEndBox.setSingleStep(5)
        self.imgEndBox.setObjectName(_fromUtf8("imgEndBox"))
        self.horizontalLayout_2.addWidget(self.imgEndBox)
        self.setEndButton = QtGui.QPushButton(self.groupBox_2)
        self.setEndButton.setMaximumSize(QtCore.QSize(65, 16777215))
        self.setEndButton.setObjectName(_fromUtf8("setEndButton"))
        self.horizontalLayout_2.addWidget(self.setEndButton)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtGui.QGroupBox(Dicom2DView)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setMinimumSize(QtCore.QSize(330, 0))
        self.groupBox_3.setMaximumSize(QtCore.QSize(330, 16777215))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.maxYBox = QtGui.QSpinBox(self.groupBox_3)
        self.maxYBox.setMaximum(9999)
        self.maxYBox.setSingleStep(5)
        self.maxYBox.setObjectName(_fromUtf8("maxYBox"))
        self.gridLayout_3.addWidget(self.maxYBox, 1, 3, 1, 1)
        self.maxXBox = QtGui.QSpinBox(self.groupBox_3)
        self.maxXBox.setMaximum(9999)
        self.maxXBox.setSingleStep(5)
        self.maxXBox.setObjectName(_fromUtf8("maxXBox"))
        self.gridLayout_3.addWidget(self.maxXBox, 1, 1, 1, 1)
        self.minYBox = QtGui.QSpinBox(self.groupBox_3)
        self.minYBox.setMaximum(9999)
        self.minYBox.setSingleStep(5)
        self.minYBox.setObjectName(_fromUtf8("minYBox"))
        self.gridLayout_3.addWidget(self.minYBox, 0, 3, 1, 1)
        self.label_7 = QtGui.QLabel(self.groupBox_3)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_3.addWidget(self.label_7, 0, 2, 1, 1)
        self.label_9 = QtGui.QLabel(self.groupBox_3)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_3.addWidget(self.label_9, 1, 2, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox_3)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_3.addWidget(self.label_6, 0, 0, 1, 1)
        self.minXBox = QtGui.QSpinBox(self.groupBox_3)
        self.minXBox.setMaximum(9999)
        self.minXBox.setSingleStep(5)
        self.minXBox.setObjectName(_fromUtf8("minXBox"))
        self.gridLayout_3.addWidget(self.minXBox, 0, 1, 1, 1)
        self.label_8 = QtGui.QLabel(self.groupBox_3)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_3.addWidget(self.label_8, 1, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.buttonBox = QtGui.QDialogButtonBox(Dicom2DView)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setMinimumSize(QtCore.QSize(330, 0))
        self.buttonBox.setMaximumSize(QtCore.QSize(330, 16777215))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.retranslateUi(Dicom2DView)
        QtCore.QMetaObject.connectSlotsByName(Dicom2DView)
        Dicom2DView.setTabOrder(self.seriesListWidget, self.imgNumBox)
        Dicom2DView.setTabOrder(self.imgNumBox, self.imgSlider)
        Dicom2DView.setTabOrder(self.imgSlider, self.imgStartBox)
        Dicom2DView.setTabOrder(self.imgStartBox, self.setStartButton)
        Dicom2DView.setTabOrder(self.setStartButton, self.imgEndBox)
        Dicom2DView.setTabOrder(self.imgEndBox, self.setEndButton)
        Dicom2DView.setTabOrder(self.setEndButton, self.minXBox)
        Dicom2DView.setTabOrder(self.minXBox, self.maxXBox)
        Dicom2DView.setTabOrder(self.maxXBox, self.minYBox)
        Dicom2DView.setTabOrder(self.minYBox, self.maxYBox)
        Dicom2DView.setTabOrder(self.maxYBox, self.buttonBox)

    def retranslateUi(self, Dicom2DView):
        Dicom2DView.setWindowTitle(_translate("Dicom2DView", "Image Crop Utility", None))
        self.stackGroup.setTitle(_translate("Dicom2DView", "Series Order (Drag to Reorder)", None))
        self.groupBox.setTitle(_translate("Dicom2DView", "Stack Image Index", None))
        self.groupBox_2.setTitle(_translate("Dicom2DView", "Stack Range", None))
        self.label_3.setText(_translate("Dicom2DView", "Start", None))
        self.setStartButton.setText(_translate("Dicom2DView", "Start", None))
        self.label_4.setText(_translate("Dicom2DView", "End", None))
        self.setEndButton.setText(_translate("Dicom2DView", "End", None))
        self.groupBox_3.setTitle(_translate("Dicom2DView", "Clip Rect", None))
        self.label_7.setText(_translate("Dicom2DView", "Min Row", None))
        self.label_9.setText(_translate("Dicom2DView", "Max Row", None))
        self.label_6.setText(_translate("Dicom2DView", "Min Col", None))
        self.label_8.setText(_translate("Dicom2DView", "Max Col", None))

