# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/dennis/Projects/rapuma/lib/rapuma/dialog/menu_project_template_dlg.ui'
#
# Created: Sun Jan 26 20:24:19 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuProjectTemplate(object):
    def setupUi(self, MenuProjectTemplate):
        MenuProjectTemplate.setObjectName("MenuProjectTemplate")
        MenuProjectTemplate.resize(279, 106)
        self.gridLayout = QtGui.QGridLayout(MenuProjectTemplate)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButtonCancel = QtGui.QPushButton(MenuProjectTemplate)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.gridLayout.addWidget(self.pushButtonCancel, 1, 2, 1, 1)
        self.pushButtonOk = QtGui.QPushButton(MenuProjectTemplate)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.gridLayout.addWidget(self.pushButtonOk, 1, 1, 1, 1)
        self.lineEditPid = QtGui.QLineEdit(MenuProjectTemplate)
        self.lineEditPid.setObjectName("lineEditPid")
        self.gridLayout.addWidget(self.lineEditPid, 0, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.labelPid = QtGui.QLabel(MenuProjectTemplate)
        self.labelPid.setObjectName("labelPid")
        self.gridLayout.addWidget(self.labelPid, 0, 0, 1, 1)

        self.retranslateUi(MenuProjectTemplate)
        QtCore.QObject.connect(self.pushButtonCancel, QtCore.SIGNAL("clicked(bool)"), MenuProjectTemplate.close)
        QtCore.QObject.connect(self.pushButtonOk, QtCore.SIGNAL("clicked()"), MenuProjectTemplate.setupUi)
        QtCore.QMetaObject.connectSlotsByName(MenuProjectTemplate)

    def retranslateUi(self, MenuProjectTemplate):
        MenuProjectTemplate.setWindowTitle(QtGui.QApplication.translate("MenuProjectTemplate", "Rapuma - Template Project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCancel.setText(QtGui.QApplication.translate("MenuProjectTemplate", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setToolTip(QtGui.QApplication.translate("MenuProjectTemplate", "Create a template from the selected project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setText(QtGui.QApplication.translate("MenuProjectTemplate", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditPid.setToolTip(QtGui.QApplication.translate("MenuProjectTemplate", "ID of the project to be removed", None, QtGui.QApplication.UnicodeUTF8))
        self.labelPid.setText(QtGui.QApplication.translate("MenuProjectTemplate", "Project ID", None, QtGui.QApplication.UnicodeUTF8))

