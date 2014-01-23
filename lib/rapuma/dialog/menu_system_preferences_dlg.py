# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'lib/rapuma/dialog/menu_system_preferences_dlg.ui'
#
# Created: Fri Jan 24 04:35:57 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuSystemPreferences(object):
    def setupUi(self, MenuSystemPreferences):
        MenuSystemPreferences.setObjectName("MenuSystemPreferences")
        MenuSystemPreferences.resize(282, 249)
        self.gridLayout = QtGui.QGridLayout(MenuSystemPreferences)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_2 = QtGui.QPushButton(MenuSystemPreferences)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 0, 1, 1)
        self.label = QtGui.QLabel(MenuSystemPreferences)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.retranslateUi(MenuSystemPreferences)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL("clicked()"), MenuSystemPreferences.close)
        QtCore.QMetaObject.connectSlotsByName(MenuSystemPreferences)

    def retranslateUi(self, MenuSystemPreferences):
        MenuSystemPreferences.setWindowTitle(QtGui.QApplication.translate("MenuSystemPreferences", "Rapuma - System Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("MenuSystemPreferences", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MenuSystemPreferences", "Sorry, this is not implemented yet!", None, QtGui.QApplication.UnicodeUTF8))

