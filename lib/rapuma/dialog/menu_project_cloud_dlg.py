# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/dennis/Projects/rapuma/lib/rapuma/dialog/menu_project_cloud_dlg.ui'
#
# Created: Sun Feb  9 20:59:38 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuProjectCloud(object):
    def setupUi(self, MenuProjectCloud):
        MenuProjectCloud.setObjectName("MenuProjectCloud")
        MenuProjectCloud.resize(448, 264)
        self.gridLayout = QtGui.QGridLayout(MenuProjectCloud)
        self.gridLayout.setObjectName("gridLayout")
        self.radioButtonPush = QtGui.QRadioButton(MenuProjectCloud)
        self.radioButtonPush.setObjectName("radioButtonPush")
        self.gridLayout.addWidget(self.radioButtonPush, 4, 0, 1, 1)
        self.pushButtonOk = QtGui.QPushButton(MenuProjectCloud)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.gridLayout.addWidget(self.pushButtonOk, 7, 2, 1, 1)
        self.pushButtonCancel = QtGui.QPushButton(MenuProjectCloud)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.gridLayout.addWidget(self.pushButtonCancel, 7, 3, 1, 1)
        self.radioButtonPull = QtGui.QRadioButton(MenuProjectCloud)
        self.radioButtonPull.setObjectName("radioButtonPull")
        self.gridLayout.addWidget(self.radioButtonPull, 5, 0, 1, 1)
        self.pushButtonLocalBrowse = QtGui.QPushButton(MenuProjectCloud)
        self.pushButtonLocalBrowse.setObjectName("pushButtonLocalBrowse")
        self.gridLayout.addWidget(self.pushButtonLocalBrowse, 1, 3, 1, 1)
        self.checkBoxBackup = QtGui.QCheckBox(MenuProjectCloud)
        self.checkBoxBackup.setObjectName("checkBoxBackup")
        self.gridLayout.addWidget(self.checkBoxBackup, 5, 1, 1, 1)
        self.pushButtonCloudBrowse = QtGui.QPushButton(MenuProjectCloud)
        self.pushButtonCloudBrowse.setObjectName("pushButtonCloudBrowse")
        self.gridLayout.addWidget(self.pushButtonCloudBrowse, 3, 3, 1, 1)
        self.radioButtonRestore = QtGui.QRadioButton(MenuProjectCloud)
        self.radioButtonRestore.setObjectName("radioButtonRestore")
        self.gridLayout.addWidget(self.radioButtonRestore, 6, 0, 1, 1)
        self.checkBoxFlush = QtGui.QCheckBox(MenuProjectCloud)
        self.checkBoxFlush.setObjectName("checkBoxFlush")
        self.gridLayout.addWidget(self.checkBoxFlush, 4, 1, 1, 1)
        self.labelPathCloud = QtGui.QLabel(MenuProjectCloud)
        self.labelPathCloud.setObjectName("labelPathCloud")
        self.gridLayout.addWidget(self.labelPathCloud, 2, 0, 1, 1)
        self.labelPathLocal = QtGui.QLabel(MenuProjectCloud)
        self.labelPathLocal.setObjectName("labelPathLocal")
        self.gridLayout.addWidget(self.labelPathLocal, 0, 0, 1, 1)
        self.lineEditProjectLocal = QtGui.QLineEdit(MenuProjectCloud)
        self.lineEditProjectLocal.setObjectName("lineEditProjectLocal")
        self.gridLayout.addWidget(self.lineEditProjectLocal, 1, 0, 1, 3)
        self.lineEditProjectCloud = QtGui.QLineEdit(MenuProjectCloud)
        self.lineEditProjectCloud.setObjectName("lineEditProjectCloud")
        self.gridLayout.addWidget(self.lineEditProjectCloud, 3, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 7, 0, 1, 2)

        self.retranslateUi(MenuProjectCloud)
        QtCore.QObject.connect(self.pushButtonCancel, QtCore.SIGNAL("clicked(bool)"), MenuProjectCloud.close)
        QtCore.QObject.connect(self.pushButtonOk, QtCore.SIGNAL("clicked()"), MenuProjectCloud.setupUi)
        QtCore.QMetaObject.connectSlotsByName(MenuProjectCloud)
        MenuProjectCloud.setTabOrder(self.pushButtonOk, self.pushButtonCancel)

    def retranslateUi(self, MenuProjectCloud):
        MenuProjectCloud.setWindowTitle(QtGui.QApplication.translate("MenuProjectCloud", "Rapuma - Manage Cloud", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonPush.setText(QtGui.QApplication.translate("MenuProjectCloud", "Local to Cloud", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setToolTip(QtGui.QApplication.translate("MenuProjectCloud", "Remove a selected project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setText(QtGui.QApplication.translate("MenuProjectCloud", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCancel.setText(QtGui.QApplication.translate("MenuProjectCloud", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonPull.setText(QtGui.QApplication.translate("MenuProjectCloud", "Cloud to Local", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonLocalBrowse.setToolTip(QtGui.QApplication.translate("MenuProjectCloud", "Browse to an existing local project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonLocalBrowse.setText(QtGui.QApplication.translate("MenuProjectCloud", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxBackup.setToolTip(QtGui.QApplication.translate("MenuProjectCloud", "Create a backup of the project before replacing it with cloud version", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxBackup.setText(QtGui.QApplication.translate("MenuProjectCloud", "Backup", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCloudBrowse.setToolTip(QtGui.QApplication.translate("MenuProjectCloud", "Browse to a project in the cloud", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCloudBrowse.setText(QtGui.QApplication.translate("MenuProjectCloud", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonRestore.setText(QtGui.QApplication.translate("MenuProjectCloud", "Restore From Cloud", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxFlush.setToolTip(QtGui.QApplication.translate("MenuProjectCloud", "Replace the cloud version with the local version", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxFlush.setText(QtGui.QApplication.translate("MenuProjectCloud", "Flush", None, QtGui.QApplication.UnicodeUTF8))
        self.labelPathCloud.setText(QtGui.QApplication.translate("MenuProjectCloud", "Path to Cloud Project", None, QtGui.QApplication.UnicodeUTF8))
        self.labelPathLocal.setText(QtGui.QApplication.translate("MenuProjectCloud", "Path to Local Project", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditProjectLocal.setToolTip(QtGui.QApplication.translate("MenuProjectCloud", "Enter the path to the local project", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditProjectLocal.setPlaceholderText(QtGui.QApplication.translate("MenuProjectCloud", "Enter Path", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditProjectCloud.setToolTip(QtGui.QApplication.translate("MenuProjectCloud", "Enter the path to the cloud project", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditProjectCloud.setPlaceholderText(QtGui.QApplication.translate("MenuProjectCloud", "Enter Path", None, QtGui.QApplication.UnicodeUTF8))

