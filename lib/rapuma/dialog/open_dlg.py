# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'lib/rapuma/dialog/open_dlg.ui'
#
# Created: Wed Jan 22 21:44:49 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_OpenProject(object):
    def setupUi(self, OpenProject):
        OpenProject.setObjectName("OpenProject")
        OpenProject.resize(282, 249)
        self.gridLayout = QtGui.QGridLayout(OpenProject)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton = QtGui.QPushButton(OpenProject)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 0, 1, 1)
        self.listViewProjects = QtGui.QListView(OpenProject)
        self.listViewProjects.setObjectName("listViewProjects")
        self.gridLayout.addWidget(self.listViewProjects, 0, 0, 1, 2)
        self.pushButton_2 = QtGui.QPushButton(OpenProject)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 1, 1, 1)

        self.retranslateUi(OpenProject)
        QtCore.QMetaObject.connectSlotsByName(OpenProject)

    def retranslateUi(self, OpenProject):
        OpenProject.setWindowTitle(QtGui.QApplication.translate("OpenProject", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("OpenProject", "Select Project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("OpenProject", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

