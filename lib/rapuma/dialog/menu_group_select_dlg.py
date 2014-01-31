# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/dennis/Projects/rapuma/lib/rapuma/dialog/menu_group_select_dlg.ui'
#
# Created: Fri Jan 31 22:00:36 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuGroupSelect(object):
    def setupUi(self, MenuGroupSelect):
        MenuGroupSelect.setObjectName("MenuGroupSelect")
        MenuGroupSelect.resize(279, 106)
        self.gridLayout = QtGui.QGridLayout(MenuGroupSelect)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButtonCancel = QtGui.QPushButton(MenuGroupSelect)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.gridLayout.addWidget(self.pushButtonCancel, 1, 2, 1, 1)
        self.pushButtonOk = QtGui.QPushButton(MenuGroupSelect)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.gridLayout.addWidget(self.pushButtonOk, 1, 1, 1, 1)
        self.lineEditGid = QtGui.QLineEdit(MenuGroupSelect)
        self.lineEditGid.setObjectName("lineEditGid")
        self.gridLayout.addWidget(self.lineEditGid, 0, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.labelGroupId = QtGui.QLabel(MenuGroupSelect)
        self.labelGroupId.setObjectName("labelGroupId")
        self.gridLayout.addWidget(self.labelGroupId, 0, 0, 1, 1)

        self.retranslateUi(MenuGroupSelect)
        QtCore.QObject.connect(self.pushButtonCancel, QtCore.SIGNAL("clicked(bool)"), MenuGroupSelect.close)
        QtCore.QObject.connect(self.pushButtonOk, QtCore.SIGNAL("clicked()"), MenuGroupSelect.setupUi)
        QtCore.QMetaObject.connectSlotsByName(MenuGroupSelect)
        MenuGroupSelect.setTabOrder(self.lineEditGid, self.pushButtonOk)
        MenuGroupSelect.setTabOrder(self.pushButtonOk, self.pushButtonCancel)

    def retranslateUi(self, MenuGroupSelect):
        MenuGroupSelect.setWindowTitle(QtGui.QApplication.translate("MenuGroupSelect", "Rapuma - Select Group", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCancel.setText(QtGui.QApplication.translate("MenuGroupSelect", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setToolTip(QtGui.QApplication.translate("MenuGroupSelect", "Remove a selected project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setText(QtGui.QApplication.translate("MenuGroupSelect", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditGid.setToolTip(QtGui.QApplication.translate("MenuGroupSelect", "ID of the group to be selected", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditGid.setStatusTip(QtGui.QApplication.translate("MenuGroupSelect", "Group ID", None, QtGui.QApplication.UnicodeUTF8))
        self.labelGroupId.setText(QtGui.QApplication.translate("MenuGroupSelect", "Group ID", None, QtGui.QApplication.UnicodeUTF8))

