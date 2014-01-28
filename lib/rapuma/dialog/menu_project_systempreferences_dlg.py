# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/dennis/Projects/rapuma/lib/rapuma/dialog/menu_project_systempreferences_dlg.ui'
#
# Created: Tue Jan 28 11:04:39 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuProjectSystempreferences(object):
    def setupUi(self, MenuProjectSystempreferences):
        MenuProjectSystempreferences.setObjectName("MenuProjectSystempreferences")
        MenuProjectSystempreferences.resize(279, 106)
        self.gridLayout = QtGui.QGridLayout(MenuProjectSystempreferences)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButtonCancel = QtGui.QPushButton(MenuProjectSystempreferences)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.gridLayout.addWidget(self.pushButtonCancel, 1, 2, 1, 1)
        self.pushButtonOk = QtGui.QPushButton(MenuProjectSystempreferences)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.gridLayout.addWidget(self.pushButtonOk, 1, 1, 1, 1)
        self.lineEditPid = QtGui.QLineEdit(MenuProjectSystempreferences)
        self.lineEditPid.setObjectName("lineEditPid")
        self.gridLayout.addWidget(self.lineEditPid, 0, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.labelPid = QtGui.QLabel(MenuProjectSystempreferences)
        self.labelPid.setObjectName("labelPid")
        self.gridLayout.addWidget(self.labelPid, 0, 0, 1, 1)

        self.retranslateUi(MenuProjectSystempreferences)
        QtCore.QObject.connect(self.pushButtonCancel, QtCore.SIGNAL("clicked(bool)"), MenuProjectSystempreferences.close)
        QtCore.QObject.connect(self.pushButtonOk, QtCore.SIGNAL("clicked()"), MenuProjectSystempreferences.setupUi)
        QtCore.QMetaObject.connectSlotsByName(MenuProjectSystempreferences)

    def retranslateUi(self, MenuProjectSystempreferences):
        MenuProjectSystempreferences.setWindowTitle(QtGui.QApplication.translate("MenuProjectSystempreferences", "Rapuma - System Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCancel.setText(QtGui.QApplication.translate("MenuProjectSystempreferences", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setToolTip(QtGui.QApplication.translate("MenuProjectSystempreferences", "Create a template from the selected project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setText(QtGui.QApplication.translate("MenuProjectSystempreferences", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditPid.setToolTip(QtGui.QApplication.translate("MenuProjectSystempreferences", "ID of the project to be removed", None, QtGui.QApplication.UnicodeUTF8))
        self.labelPid.setText(QtGui.QApplication.translate("MenuProjectSystempreferences", "Project ID", None, QtGui.QApplication.UnicodeUTF8))

