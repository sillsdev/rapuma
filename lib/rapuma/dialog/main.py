# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'lib/rapuma/dialog/main.ui'
#
# Created: Sat Jan  4 23:11:23 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.menuFileOpen = QtGui.QAction(MainWindow)
        self.menuFileOpen.setObjectName("menuFileOpen")
        self.menuFileNew = QtGui.QAction(MainWindow)
        self.menuFileNew.setObjectName("menuFileNew")
        self.menuFileQuite = QtGui.QAction(MainWindow)
        self.menuFileQuite.setObjectName("menuFileQuite")
        self.menuHelpAbout = QtGui.QAction(MainWindow)
        self.menuHelpAbout.setObjectName("menuHelpAbout")
        self.menuFile.addAction(self.menuFileOpen)
        self.menuFile.addAction(self.menuFileNew)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.menuFileQuite)
        self.menuHelp.addAction(self.menuHelpAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Rapuma", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate("MainWindow", "open", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFileOpen.setText(QtGui.QApplication.translate("MainWindow", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFileOpen.setToolTip(QtGui.QApplication.translate("MainWindow", "Open an exsiting project", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFileNew.setText(QtGui.QApplication.translate("MainWindow", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFileNew.setToolTip(QtGui.QApplication.translate("MainWindow", "Create a new Rapuma project", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFileQuite.setText(QtGui.QApplication.translate("MainWindow", "Quite", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFileQuite.setToolTip(QtGui.QApplication.translate("MainWindow", "Quite Rapuma", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelpAbout.setText(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))

