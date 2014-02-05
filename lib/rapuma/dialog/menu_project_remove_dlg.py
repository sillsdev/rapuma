# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/dennis/Projects/rapuma/lib/rapuma/dialog/menu_project_remove_dlg.ui'
#
# Created: Wed Feb  5 11:13:04 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuProjectRemove(object):
    def setupUi(self, MenuProjectRemove):
        MenuProjectRemove.setObjectName("MenuProjectRemove")
        MenuProjectRemove.resize(279, 106)
        self.gridLayout = QtGui.QGridLayout(MenuProjectRemove)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.pushButtonOk = QtGui.QPushButton(MenuProjectRemove)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.gridLayout.addWidget(self.pushButtonOk, 2, 1, 1, 1)
        self.pushButtonCancel = QtGui.QPushButton(MenuProjectRemove)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.gridLayout.addWidget(self.pushButtonCancel, 2, 2, 1, 1)
        self.labelPid = QtGui.QLabel(MenuProjectRemove)
        self.labelPid.setObjectName("labelPid")
        self.gridLayout.addWidget(self.labelPid, 0, 0, 1, 1)
        self.checkBoxBackup = QtGui.QCheckBox(MenuProjectRemove)
        self.checkBoxBackup.setObjectName("checkBoxBackup")
        self.gridLayout.addWidget(self.checkBoxBackup, 1, 0, 1, 1)
        self.lineEditPid = QtGui.QLineEdit(MenuProjectRemove)
        self.lineEditPid.setObjectName("lineEditPid")
        self.gridLayout.addWidget(self.lineEditPid, 0, 1, 1, 2)

        self.retranslateUi(MenuProjectRemove)
        QtCore.QObject.connect(self.pushButtonCancel, QtCore.SIGNAL("clicked(bool)"), MenuProjectRemove.close)
        QtCore.QObject.connect(self.pushButtonOk, QtCore.SIGNAL("clicked()"), MenuProjectRemove.setupUi)
        QtCore.QObject.connect(self.checkBoxBackup, QtCore.SIGNAL("toggled(bool)"), MenuProjectRemove.setupUi)
        QtCore.QMetaObject.connectSlotsByName(MenuProjectRemove)

    def retranslateUi(self, MenuProjectRemove):
        MenuProjectRemove.setWindowTitle(QtGui.QApplication.translate("MenuProjectRemove", "Rapuma - Remove Project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setToolTip(QtGui.QApplication.translate("MenuProjectRemove", "Remove a selected project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setText(QtGui.QApplication.translate("MenuProjectRemove", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCancel.setText(QtGui.QApplication.translate("MenuProjectRemove", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.labelPid.setText(QtGui.QApplication.translate("MenuProjectRemove", "Project ID", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxBackup.setToolTip(QtGui.QApplication.translate("MenuProjectRemove", "Create a backup of the project before removing it", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxBackup.setText(QtGui.QApplication.translate("MenuProjectRemove", "Backup", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditPid.setToolTip(QtGui.QApplication.translate("MenuProjectRemove", "ID of the project to be removed", None, QtGui.QApplication.UnicodeUTF8))

