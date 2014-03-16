# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/dennis/Projects/rapuma/lib/rapuma/dialog/menu_project_remove_dlg.ui'
#
# Created: Sat Mar 15 22:37:41 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuProjectRemove(object):
    def setupUi(self, MenuProjectRemove):
        MenuProjectRemove.setObjectName("MenuProjectRemove")
        MenuProjectRemove.resize(550, 285)
        self.gridLayout = QtGui.QGridLayout(MenuProjectRemove)
        self.gridLayout.setObjectName("gridLayout")
        self.labelRemoveProject = QtGui.QLabel(MenuProjectRemove)
        self.labelRemoveProject.setObjectName("labelRemoveProject")
        self.gridLayout.addWidget(self.labelRemoveProject, 0, 0, 1, 1)
        self.listWidgetProjects = QtGui.QListWidget(MenuProjectRemove)
        self.listWidgetProjects.setObjectName("listWidgetProjects")
        self.gridLayout.addWidget(self.listWidgetProjects, 1, 0, 1, 3)
        self.checkBoxBackup = QtGui.QCheckBox(MenuProjectRemove)
        self.checkBoxBackup.setChecked(True)
        self.checkBoxBackup.setObjectName("checkBoxBackup")
        self.gridLayout.addWidget(self.checkBoxBackup, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.pushButtonOk = QtGui.QPushButton(MenuProjectRemove)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.gridLayout.addWidget(self.pushButtonOk, 3, 1, 1, 1)
        self.pushButtonCancel = QtGui.QPushButton(MenuProjectRemove)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.gridLayout.addWidget(self.pushButtonCancel, 3, 2, 1, 1)

        self.retranslateUi(MenuProjectRemove)
        QtCore.QObject.connect(self.pushButtonCancel, QtCore.SIGNAL("clicked(bool)"), MenuProjectRemove.close)
        QtCore.QObject.connect(self.pushButtonOk, QtCore.SIGNAL("clicked()"), MenuProjectRemove.update)
        QtCore.QMetaObject.connectSlotsByName(MenuProjectRemove)
        MenuProjectRemove.setTabOrder(self.pushButtonOk, self.pushButtonCancel)

    def retranslateUi(self, MenuProjectRemove):
        MenuProjectRemove.setWindowTitle(QtGui.QApplication.translate("MenuProjectRemove", "Rapuma - Select Project", None, QtGui.QApplication.UnicodeUTF8))
        self.labelRemoveProject.setText(QtGui.QApplication.translate("MenuProjectRemove", "Select A Project To Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.listWidgetProjects.setToolTip(QtGui.QApplication.translate("MenuProjectRemove", "Select a project to remove", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxBackup.setToolTip(QtGui.QApplication.translate("MenuProjectRemove", "Create a backup of the project before removing it", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxBackup.setText(QtGui.QApplication.translate("MenuProjectRemove", "Backup", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setToolTip(QtGui.QApplication.translate("MenuProjectRemove", "Remove a selected project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setText(QtGui.QApplication.translate("MenuProjectRemove", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCancel.setText(QtGui.QApplication.translate("MenuProjectRemove", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

