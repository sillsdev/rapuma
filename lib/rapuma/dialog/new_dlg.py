# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'lib/rapuma/dialog/new_dlg.ui'
#
# Created: Mon Jan 20 16:38:57 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_NewProject(object):
    def setupUi(self, NewProject):
        NewProject.setObjectName("NewProject")
        NewProject.resize(687, 393)
        self.pushButton = QtGui.QPushButton(NewProject)
        self.pushButton.setGeometry(QtCore.QRect(420, 350, 98, 27))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtGui.QPushButton(NewProject)
        self.pushButton_2.setGeometry(QtCore.QRect(550, 350, 98, 27))
        self.pushButton_2.setObjectName("pushButton_2")
        self.textEditProjectID = QtGui.QPlainTextEdit(NewProject)
        self.textEditProjectID.setGeometry(QtCore.QRect(20, 20, 181, 31))
        self.textEditProjectID.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEditProjectID.setObjectName("textEditProjectID")

        self.retranslateUi(NewProject)
        QtCore.QMetaObject.connectSlotsByName(NewProject)

    def retranslateUi(self, NewProject):
        NewProject.setWindowTitle(QtGui.QApplication.translate("NewProject", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("NewProject", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("NewProject", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

