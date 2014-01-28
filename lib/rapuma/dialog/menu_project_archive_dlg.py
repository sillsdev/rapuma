# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/dennis/Projects/rapuma/lib/rapuma/dialog/menu_project_archive_dlg.ui'
#
# Created: Tue Jan 28 11:04:38 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuProjectArchive(object):
    def setupUi(self, MenuProjectArchive):
        MenuProjectArchive.setObjectName("MenuProjectArchive")
        MenuProjectArchive.resize(279, 106)
        self.gridLayout = QtGui.QGridLayout(MenuProjectArchive)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButtonCancel = QtGui.QPushButton(MenuProjectArchive)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.gridLayout.addWidget(self.pushButtonCancel, 1, 2, 1, 1)
        self.pushButtonOk = QtGui.QPushButton(MenuProjectArchive)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.gridLayout.addWidget(self.pushButtonOk, 1, 1, 1, 1)
        self.lineEditPid = QtGui.QLineEdit(MenuProjectArchive)
        self.lineEditPid.setObjectName("lineEditPid")
        self.gridLayout.addWidget(self.lineEditPid, 0, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.labelPid = QtGui.QLabel(MenuProjectArchive)
        self.labelPid.setObjectName("labelPid")
        self.gridLayout.addWidget(self.labelPid, 0, 0, 1, 1)

        self.retranslateUi(MenuProjectArchive)
        QtCore.QObject.connect(self.pushButtonCancel, QtCore.SIGNAL("clicked(bool)"), MenuProjectArchive.close)
        QtCore.QObject.connect(self.pushButtonOk, QtCore.SIGNAL("clicked()"), MenuProjectArchive.setupUi)
        QtCore.QMetaObject.connectSlotsByName(MenuProjectArchive)

    def retranslateUi(self, MenuProjectArchive):
        MenuProjectArchive.setWindowTitle(QtGui.QApplication.translate("MenuProjectArchive", "Rapuma - Archive Project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCancel.setText(QtGui.QApplication.translate("MenuProjectArchive", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setToolTip(QtGui.QApplication.translate("MenuProjectArchive", "Create a template from the selected project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setText(QtGui.QApplication.translate("MenuProjectArchive", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditPid.setToolTip(QtGui.QApplication.translate("MenuProjectArchive", "ID of the project to be removed", None, QtGui.QApplication.UnicodeUTF8))
        self.labelPid.setText(QtGui.QApplication.translate("MenuProjectArchive", "Project ID", None, QtGui.QApplication.UnicodeUTF8))

