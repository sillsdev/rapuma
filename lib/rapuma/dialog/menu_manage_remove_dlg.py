# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'lib/rapuma/dialog/menu_manage_remove_dlg.ui'
#
# Created: Fri Jan 24 04:35:57 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuManageRemove(object):
    def setupUi(self, MenuManageRemove):
        MenuManageRemove.setObjectName("MenuManageRemove")
        MenuManageRemove.resize(282, 249)
        self.gridLayout = QtGui.QGridLayout(MenuManageRemove)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_2 = QtGui.QPushButton(MenuManageRemove)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 0, 1, 1)
        self.label = QtGui.QLabel(MenuManageRemove)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(MenuManageRemove)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL("clicked()"), MenuManageRemove.close)
        QtCore.QMetaObject.connectSlotsByName(MenuManageRemove)

    def retranslateUi(self, MenuManageRemove):
        MenuManageRemove.setWindowTitle(QtGui.QApplication.translate("MenuManageRemove", "Rapuma - Remove Project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("MenuManageRemove", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MenuManageRemove", "Sorry, this is not implemented yet!", None, QtGui.QApplication.UnicodeUTF8))

