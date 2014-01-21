#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Copyright 2014, SIL International
#    All rights reserved.
#
#    This library is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation; either version 2.1 of License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should also have received a copy of the GNU Lesser General Public
#    License along with this library in the file named "LICENSE".
#    If not, write to the Free Software Foundation, 51 Franklin Street,
#    suite 500, Boston, MA 02110-1335, USA or visit their web page on the 
#    internet at http://www.fsf.org/licenses/lgpl.html.


import os, sys

# Load GUI modules
from PySide                             import QtGui, QtCore
from PySide.QtGui                       import QDialog, QApplication, QMessageBox
from PySide.QtCore                      import QPropertyAnimation
from rapuma.dialog                      import new_dlg

class NewCtrl (QDialog, QPropertyAnimation, new_dlg.Ui_NewProject) :

    def __init__ (self, parent=None) :
        '''Initialize and start up the UI'''

        super(NewCtrl, self).__init__(parent)

        self.setupUi(self)
        self.connectionActions()


    def main (self) :
        '''This function shows the main dialog'''

        self.show()


    def connectionActions (self) :
        '''Connect to form buttons.'''

        self.pushButtonOk.clicked.connect(self.okClicked)
        self.pushButtonBrowse.clicked.connect(self.browseForFolder)


    def okClicked (self) :
        '''Execute the OK button.'''

        projPath                = self.lineEditProjPath.text()

        print "OK button was pushed", projPath


    def browseForFolder (self) :
        '''Call a basic find file widget to get the folder we want to put this project in.'''

        # Set our browse options
        options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        # Run the dialog and get the folder
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                "QFileDialog.getExistingDirectory()",
                self.lineEditProjPath.text(), options)
        # Set the text in the edit box
        if directory :
            self.lineEditProjPath.setText(directory)


###############################################################################
################################ Menu Items ###################################
###############################################################################



###############################################################################
############################## Dialog Starts Here #############################
###############################################################################

if __name__ == '__main__' :

    app = QApplication(sys.argv)
    window = NewCtrl()
    window.main()
    sys.exit(app.exec_())












