# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'lib/rapuma/dialog/open.ui'
#
# Created: Fri Jan 10 20:17:53 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_OpenProjectDialog(object):
    def setupUi(self, OpenProjectDialog):
        OpenProjectDialog.setObjectName("OpenProjectDialog")
        OpenProjectDialog.resize(282, 249)
        self.gridLayout = QtGui.QGridLayout(OpenProjectDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton = QtGui.QPushButton(OpenProjectDialog)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 0, 1, 1)
        self.listViewProjects = QtGui.QListView(OpenProjectDialog)
        self.listViewProjects.setObjectName("listViewProjects")
        self.gridLayout.addWidget(self.listViewProjects, 0, 0, 1, 2)
        self.pushButton_2 = QtGui.QPushButton(OpenProjectDialog)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 1, 1, 1)

        self.retranslateUi(OpenProjectDialog)
        QtCore.QMetaObject.connectSlotsByName(OpenProjectDialog)

    def retranslateUi(self, OpenProjectDialog):
        OpenProjectDialog.setWindowTitle(QtGui.QApplication.translate("OpenProjectDialog", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("OpenProjectDialog", "Select Project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("OpenProjectDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

