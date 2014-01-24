# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'lib/rapuma/dialog/menu_manage_backup_dlg.ui'
#
# Created: Fri Jan 24 21:44:55 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuManageBackup(object):
    def setupUi(self, MenuManageBackup):
        MenuManageBackup.setObjectName("MenuManageBackup")
        MenuManageBackup.resize(282, 249)
        self.gridLayout = QtGui.QGridLayout(MenuManageBackup)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_2 = QtGui.QPushButton(MenuManageBackup)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 0, 1, 1)
        self.label = QtGui.QLabel(MenuManageBackup)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(MenuManageBackup)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL("clicked()"), MenuManageBackup.close)
        QtCore.QMetaObject.connectSlotsByName(MenuManageBackup)

    def retranslateUi(self, MenuManageBackup):
        MenuManageBackup.setWindowTitle(QtGui.QApplication.translate("MenuManageBackup", "Rapuma - Backup Project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("MenuManageBackup", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MenuManageBackup", "Sorry, this is not implemented yet!", None, QtGui.QApplication.UnicodeUTF8))

