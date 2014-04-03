# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/dennis/Projects/rapuma/lib/rapuma/dialog/menu_project_select_dlg.ui'
#
# Created: Thu Apr  3 20:53:28 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuProjectSelect(object):
    def setupUi(self, MenuProjectSelect):
        MenuProjectSelect.setObjectName("MenuProjectSelect")
        MenuProjectSelect.resize(550, 285)
        self.gridLayout = QtGui.QGridLayout(MenuProjectSelect)
        self.gridLayout.setObjectName("gridLayout")
        self.labelSelectProject = QtGui.QLabel(MenuProjectSelect)
        self.labelSelectProject.setObjectName("labelSelectProject")
        self.gridLayout.addWidget(self.labelSelectProject, 0, 0, 1, 2)
        self.listWidgetProjects = QtGui.QListWidget(MenuProjectSelect)
        self.listWidgetProjects.setObjectName("listWidgetProjects")
        self.gridLayout.addWidget(self.listWidgetProjects, 1, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.pushButtonOk = QtGui.QPushButton(MenuProjectSelect)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.gridLayout.addWidget(self.pushButtonOk, 2, 1, 1, 1)
        self.pushButtonCancel = QtGui.QPushButton(MenuProjectSelect)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.gridLayout.addWidget(self.pushButtonCancel, 2, 2, 1, 1)

        self.retranslateUi(MenuProjectSelect)
        QtCore.QObject.connect(self.pushButtonCancel, QtCore.SIGNAL("clicked(bool)"), MenuProjectSelect.close)
        QtCore.QObject.connect(self.pushButtonOk, QtCore.SIGNAL("clicked()"), MenuProjectSelect.update)
        QtCore.QMetaObject.connectSlotsByName(MenuProjectSelect)
        MenuProjectSelect.setTabOrder(self.pushButtonOk, self.pushButtonCancel)

    def retranslateUi(self, MenuProjectSelect):
        MenuProjectSelect.setWindowTitle(QtGui.QApplication.translate("MenuProjectSelect", "Rapuma - Select Project", None, QtGui.QApplication.UnicodeUTF8))
        self.labelSelectProject.setText(QtGui.QApplication.translate("MenuProjectSelect", "Select A Project", None, QtGui.QApplication.UnicodeUTF8))
        self.listWidgetProjects.setToolTip(QtGui.QApplication.translate("MenuProjectSelect", "Select a project to work on", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setToolTip(QtGui.QApplication.translate("MenuProjectSelect", "Remove a selected project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setText(QtGui.QApplication.translate("MenuProjectSelect", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCancel.setText(QtGui.QApplication.translate("MenuProjectSelect", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

