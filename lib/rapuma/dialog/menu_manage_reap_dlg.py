# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'lib/rapuma/dialog/menu_manage_reap_dlg.ui'
#
# Created: Fri Jan 24 21:44:56 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuManageReap(object):
    def setupUi(self, MenuManageReap):
        MenuManageReap.setObjectName("MenuManageReap")
        MenuManageReap.resize(282, 249)
        self.gridLayout = QtGui.QGridLayout(MenuManageReap)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_2 = QtGui.QPushButton(MenuManageReap)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 0, 1, 1)
        self.label = QtGui.QLabel(MenuManageReap)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(MenuManageReap)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL("clicked()"), MenuManageReap.close)
        QtCore.QMetaObject.connectSlotsByName(MenuManageReap)

    def retranslateUi(self, MenuManageReap):
        MenuManageReap.setWindowTitle(QtGui.QApplication.translate("MenuManageReap", "Rapuma - REAP Project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("MenuManageReap", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MenuManageReap", "Sorry, this is not implemented yet!", None, QtGui.QApplication.UnicodeUTF8))

