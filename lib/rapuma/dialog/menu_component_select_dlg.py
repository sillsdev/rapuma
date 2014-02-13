# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/dennis/Projects/rapuma/lib/rapuma/dialog/menu_component_select_dlg.ui'
#
# Created: Thu Feb 13 09:49:17 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuComponentSelect(object):
    def setupUi(self, MenuComponentSelect):
        MenuComponentSelect.setObjectName("MenuComponentSelect")
        MenuComponentSelect.resize(298, 188)
        self.gridLayout = QtGui.QGridLayout(MenuComponentSelect)
        self.gridLayout.setObjectName("gridLayout")
        self.labelComponentId = QtGui.QLabel(MenuComponentSelect)
        self.labelComponentId.setObjectName("labelComponentId")
        self.gridLayout.addWidget(self.labelComponentId, 0, 0, 1, 1)
        self.listWidgetComponents = QtGui.QListWidget(MenuComponentSelect)
        self.listWidgetComponents.setObjectName("listWidgetComponents")
        self.gridLayout.addWidget(self.listWidgetComponents, 1, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.pushButtonOk = QtGui.QPushButton(MenuComponentSelect)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.gridLayout.addWidget(self.pushButtonOk, 2, 1, 1, 1)
        self.pushButtonCancel = QtGui.QPushButton(MenuComponentSelect)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.gridLayout.addWidget(self.pushButtonCancel, 2, 2, 1, 1)

        self.retranslateUi(MenuComponentSelect)
        QtCore.QObject.connect(self.pushButtonCancel, QtCore.SIGNAL("clicked(bool)"), MenuComponentSelect.close)
        QtCore.QObject.connect(self.pushButtonOk, QtCore.SIGNAL("clicked()"), MenuComponentSelect.setupUi)
        QtCore.QMetaObject.connectSlotsByName(MenuComponentSelect)
        MenuComponentSelect.setTabOrder(self.pushButtonOk, self.pushButtonCancel)

    def retranslateUi(self, MenuComponentSelect):
        MenuComponentSelect.setWindowTitle(QtGui.QApplication.translate("MenuComponentSelect", "Rapuma - Select Component", None, QtGui.QApplication.UnicodeUTF8))
        self.labelComponentId.setText(QtGui.QApplication.translate("MenuComponentSelect", "Component ID", None, QtGui.QApplication.UnicodeUTF8))
        self.listWidgetComponents.setToolTip(QtGui.QApplication.translate("MenuComponentSelect", "Select a component", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setToolTip(QtGui.QApplication.translate("MenuComponentSelect", "Remove a selected project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setText(QtGui.QApplication.translate("MenuComponentSelect", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCancel.setText(QtGui.QApplication.translate("MenuComponentSelect", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

