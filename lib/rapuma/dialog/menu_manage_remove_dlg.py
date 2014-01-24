# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'lib/rapuma/dialog/menu_manage_remove_dlg.ui'
#
# Created: Fri Jan 24 21:44:56 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuManageRemove(object):
    def setupUi(self, MenuManageRemove):
        MenuManageRemove.setObjectName("MenuManageRemove")
        MenuManageRemove.resize(279, 106)
        self.gridLayout = QtGui.QGridLayout(MenuManageRemove)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.pushButtonOk = QtGui.QPushButton(MenuManageRemove)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.gridLayout.addWidget(self.pushButtonOk, 2, 1, 1, 1)
        self.pushButtonCancel = QtGui.QPushButton(MenuManageRemove)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.gridLayout.addWidget(self.pushButtonCancel, 2, 2, 1, 1)
        self.labelPid = QtGui.QLabel(MenuManageRemove)
        self.labelPid.setObjectName("labelPid")
        self.gridLayout.addWidget(self.labelPid, 0, 0, 1, 1)
        self.checkBoxBackup = QtGui.QCheckBox(MenuManageRemove)
        self.checkBoxBackup.setObjectName("checkBoxBackup")
        self.gridLayout.addWidget(self.checkBoxBackup, 1, 0, 1, 1)
        self.lineEditPid = QtGui.QLineEdit(MenuManageRemove)
        self.lineEditPid.setObjectName("lineEditPid")
        self.gridLayout.addWidget(self.lineEditPid, 0, 1, 1, 2)

        self.retranslateUi(MenuManageRemove)
        QtCore.QObject.connect(self.pushButtonCancel, QtCore.SIGNAL("clicked(bool)"), MenuManageRemove.close)
        QtCore.QObject.connect(self.pushButtonOk, QtCore.SIGNAL("clicked()"), MenuManageRemove.setupUi)
        QtCore.QObject.connect(self.checkBoxBackup, QtCore.SIGNAL("toggled(bool)"), MenuManageRemove.setupUi)
        QtCore.QMetaObject.connectSlotsByName(MenuManageRemove)

    def retranslateUi(self, MenuManageRemove):
        MenuManageRemove.setWindowTitle(QtGui.QApplication.translate("MenuManageRemove", "Rapuma - Remove Project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setToolTip(QtGui.QApplication.translate("MenuManageRemove", "Remove a selected project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setText(QtGui.QApplication.translate("MenuManageRemove", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCancel.setText(QtGui.QApplication.translate("MenuManageRemove", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.labelPid.setText(QtGui.QApplication.translate("MenuManageRemove", "Project ID", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxBackup.setToolTip(QtGui.QApplication.translate("MenuManageRemove", "Create a backup of the project before removing it", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxBackup.setText(QtGui.QApplication.translate("MenuManageRemove", "Backup", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditPid.setToolTip(QtGui.QApplication.translate("MenuManageRemove", "ID of the project to be removed", None, QtGui.QApplication.UnicodeUTF8))

