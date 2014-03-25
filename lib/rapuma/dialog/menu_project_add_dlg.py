# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/dennis/Projects/rapuma/lib/rapuma/dialog/menu_project_add_dlg.ui'
#
# Created: Tue Mar 25 08:08:47 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MenuProjectAdd(object):
    def setupUi(self, MenuProjectAdd):
        MenuProjectAdd.setObjectName("MenuProjectAdd")
        MenuProjectAdd.resize(519, 157)
        self.gridLayout = QtGui.QGridLayout(MenuProjectAdd)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEditLangId = QtGui.QLineEdit(MenuProjectAdd)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditLangId.sizePolicy().hasHeightForWidth())
        self.lineEditLangId.setSizePolicy(sizePolicy)
        self.lineEditLangId.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.lineEditLangId.setWhatsThis("")
        self.lineEditLangId.setText("")
        self.lineEditLangId.setMaxLength(3)
        self.lineEditLangId.setObjectName("lineEditLangId")
        self.gridLayout.addWidget(self.lineEditLangId, 1, 0, 1, 1)
        self.labelIdentification = QtGui.QLabel(MenuProjectAdd)
        self.labelIdentification.setObjectName("labelIdentification")
        self.gridLayout.addWidget(self.labelIdentification, 0, 0, 1, 1)
        self.lineEditScriptId = QtGui.QLineEdit(MenuProjectAdd)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditScriptId.sizePolicy().hasHeightForWidth())
        self.lineEditScriptId.setSizePolicy(sizePolicy)
        self.lineEditScriptId.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.lineEditScriptId.setText("")
        self.lineEditScriptId.setMaxLength(4)
        self.lineEditScriptId.setObjectName("lineEditScriptId")
        self.gridLayout.addWidget(self.lineEditScriptId, 1, 2, 1, 2)
        self.labelDash_2 = QtGui.QLabel(MenuProjectAdd)
        self.labelDash_2.setAlignment(QtCore.Qt.AlignCenter)
        self.labelDash_2.setObjectName("labelDash_2")
        self.gridLayout.addWidget(self.labelDash_2, 1, 4, 1, 1)
        self.labelDash_1 = QtGui.QLabel(MenuProjectAdd)
        self.labelDash_1.setAlignment(QtCore.Qt.AlignCenter)
        self.labelDash_1.setObjectName("labelDash_1")
        self.gridLayout.addWidget(self.labelDash_1, 1, 1, 1, 1)
        self.lineEditProjId = QtGui.QLineEdit(MenuProjectAdd)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditProjId.sizePolicy().hasHeightForWidth())
        self.lineEditProjId.setSizePolicy(sizePolicy)
        self.lineEditProjId.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.lineEditProjId.setText("")
        self.lineEditProjId.setMaxLength(10)
        self.lineEditProjId.setObjectName("lineEditProjId")
        self.gridLayout.addWidget(self.lineEditProjId, 1, 5, 1, 2)
        self.labelPath = QtGui.QLabel(MenuProjectAdd)
        self.labelPath.setObjectName("labelPath")
        self.gridLayout.addWidget(self.labelPath, 2, 0, 1, 1)
        self.lineEditProjPath = QtGui.QLineEdit(MenuProjectAdd)
        self.lineEditProjPath.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.lineEditProjPath.setText("")
        self.lineEditProjPath.setObjectName("lineEditProjPath")
        self.gridLayout.addWidget(self.lineEditProjPath, 3, 0, 1, 6)
        self.pushButtonBrowse = QtGui.QPushButton(MenuProjectAdd)
        self.pushButtonBrowse.setObjectName("pushButtonBrowse")
        self.gridLayout.addWidget(self.pushButtonBrowse, 3, 6, 1, 1)
        self.pushButtonCancel = QtGui.QPushButton(MenuProjectAdd)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.gridLayout.addWidget(self.pushButtonCancel, 4, 6, 1, 1)
        self.pushButtonOk = QtGui.QPushButton(MenuProjectAdd)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.gridLayout.addWidget(self.pushButtonOk, 4, 4, 1, 2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 4)

        self.retranslateUi(MenuProjectAdd)
        QtCore.QObject.connect(self.pushButtonCancel, QtCore.SIGNAL("clicked(bool)"), MenuProjectAdd.close)
        QtCore.QObject.connect(self.pushButtonOk, QtCore.SIGNAL("clicked()"), MenuProjectAdd.update)
        QtCore.QObject.connect(self.pushButtonBrowse, QtCore.SIGNAL("clicked()"), MenuProjectAdd.update)
        QtCore.QMetaObject.connectSlotsByName(MenuProjectAdd)
        MenuProjectAdd.setTabOrder(self.pushButtonCancel, self.lineEditLangId)
        MenuProjectAdd.setTabOrder(self.lineEditLangId, self.lineEditScriptId)
        MenuProjectAdd.setTabOrder(self.lineEditScriptId, self.lineEditProjId)
        MenuProjectAdd.setTabOrder(self.lineEditProjId, self.lineEditProjPath)
        MenuProjectAdd.setTabOrder(self.lineEditProjPath, self.pushButtonBrowse)
        MenuProjectAdd.setTabOrder(self.pushButtonBrowse, self.pushButtonOk)

    def retranslateUi(self, MenuProjectAdd):
        MenuProjectAdd.setWindowTitle(QtGui.QApplication.translate("MenuProjectAdd", "Rapuma - New Project", None, QtGui.QApplication.UnicodeUTF8))
        MenuProjectAdd.setToolTip(QtGui.QApplication.translate("MenuProjectAdd", "Create a new Rapuma project", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditLangId.setToolTip(QtGui.QApplication.translate("MenuProjectAdd", "Ethnologue 3 letter language code", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditLangId.setPlaceholderText(QtGui.QApplication.translate("MenuProjectAdd", "Language", None, QtGui.QApplication.UnicodeUTF8))
        self.labelIdentification.setText(QtGui.QApplication.translate("MenuProjectAdd", "Identification", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditScriptId.setToolTip(QtGui.QApplication.translate("MenuProjectAdd", "ISO 4 letter script code", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditScriptId.setPlaceholderText(QtGui.QApplication.translate("MenuProjectAdd", "Script", None, QtGui.QApplication.UnicodeUTF8))
        self.labelDash_2.setText(QtGui.QApplication.translate("MenuProjectAdd", "—", None, QtGui.QApplication.UnicodeUTF8))
        self.labelDash_1.setText(QtGui.QApplication.translate("MenuProjectAdd", "—", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditProjId.setToolTip(QtGui.QApplication.translate("MenuProjectAdd", "Create a unique project identifier code (max 10 letters)", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditProjId.setPlaceholderText(QtGui.QApplication.translate("MenuProjectAdd", "Project ID", None, QtGui.QApplication.UnicodeUTF8))
        self.labelPath.setText(QtGui.QApplication.translate("MenuProjectAdd", "Path", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditProjPath.setToolTip(QtGui.QApplication.translate("MenuProjectAdd", "Browse to the project path", None, QtGui.QApplication.UnicodeUTF8))
        self.lineEditProjPath.setPlaceholderText(QtGui.QApplication.translate("MenuProjectAdd", "Project Path", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonBrowse.setToolTip(QtGui.QApplication.translate("MenuProjectAdd", "Browse to the project folder", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonBrowse.setText(QtGui.QApplication.translate("MenuProjectAdd", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCancel.setToolTip(QtGui.QApplication.translate("MenuProjectAdd", "Click to cancel project creation", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonCancel.setText(QtGui.QApplication.translate("MenuProjectAdd", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setToolTip(QtGui.QApplication.translate("MenuProjectAdd", "Click to create a new project", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonOk.setText(QtGui.QApplication.translate("MenuProjectAdd", "OK", None, QtGui.QApplication.UnicodeUTF8))

