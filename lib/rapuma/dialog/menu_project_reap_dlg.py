# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/dennis/Projects/rapuma/lib/rapuma/dialog/menu_project_reap_dlg.ui'
#
# Created: Tue Jan 28 11:04:38 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuProjectReap(object):
    def setupUi(self, MenuProjectReap):
        MenuProjectReap.setObjectName("MenuProjectReap")
        MenuProjectReap.resize(279, 106)
        self.gridLayout = QtGui.QGridLayout(MenuProjectReap)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButtonCancel = QtGui.QPushButton(MenuProjectReap)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.gridLayout.addWidget(self.pushButtonCancel, 1, 2, 1, 1)
        self.pushButtonOk = QtGui.QPushButton(MenuProjectReap)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.gridLayout.addWidget(self.pushButtonOk, 1, 1, 1, 1)
        self.lineEditPid = QtGui.QLineEdit(MenuProjectReap)
        self.lineEditPid.setObjectName("lineEditPid")
        self.gridLayout.addWidget(self.lineEditPid, 0, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.labelPid = QtGui.QLabel(MenuProjectReap)
        self.labelPid.setObjectName("labelPid")
        self.gridLayout.addWidget(self.labelPid, 0, 0, 1, 1)

        self.retranslateUi(MenuProjectReap)
        QtCore.QObject.connect(self.pushButtonCancel, QtCore.SIGNAL("clicked(bool)"), MenuProjectReap.close)
        QtCore.QObject.connect(self.pushButtonOk, QtCore.SIGNAL("clicked()"), MenuProjectReap.setupUi)
        QtCore.QMetaObject.connectSlotsByName(MenuProjectReap)

    def retranslateUi(self, MenuProjectReap):
        MenuProjectReap.setWindowTitle(QtGui.QApplication.translate("MenuProjectReap", "Rapuma - REAP Project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCancel.setText(QtGui.QApplication.translate("MenuProjectReap", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setToolTip(QtGui.QApplication.translate("MenuProjectReap", "Create a template from the selected project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setText(QtGui.QApplication.translate("MenuProjectReap", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditPid.setToolTip(QtGui.QApplication.translate("MenuProjectReap", "ID of the project to be removed", None, QtGui.QApplication.UnicodeUTF8))
        self.labelPid.setText(QtGui.QApplication.translate("MenuProjectReap", "Project ID", None, QtGui.QApplication.UnicodeUTF8))

