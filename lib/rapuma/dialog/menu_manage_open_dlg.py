# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'lib/rapuma/dialog/menu_manage_open_dlg.ui'
#
# Created: Fri Jan 24 04:35:57 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuManageOpen(object):
    def setupUi(self, MenuManageOpen):
        MenuManageOpen.setObjectName("MenuManageOpen")
        MenuManageOpen.resize(282, 249)
        self.gridLayout = QtGui.QGridLayout(MenuManageOpen)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_2 = QtGui.QPushButton(MenuManageOpen)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 0, 1, 1)
        self.label = QtGui.QLabel(MenuManageOpen)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(MenuManageOpen)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL("clicked()"), MenuManageOpen.close)
        QtCore.QMetaObject.connectSlotsByName(MenuManageOpen)

    def retranslateUi(self, MenuManageOpen):
        MenuManageOpen.setWindowTitle(QtGui.QApplication.translate("MenuManageOpen", "Rapuma - Open Project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("MenuManageOpen", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MenuManageOpen", "Sorry, this is not implemented yet!", None, QtGui.QApplication.UnicodeUTF8))

