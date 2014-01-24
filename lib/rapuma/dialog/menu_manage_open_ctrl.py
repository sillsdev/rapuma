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


import os, sys, StringIO

# Load GUI modules
from PySide                             import QtGui, QtCore
from PySide.QtGui                       import QDialog, QApplication, QMessageBox
from PySide.QtCore                      import QPropertyAnimation
from rapuma.dialog                      import menu_manage_open_dlg

class MenuManageOpenCtrl (QDialog, QPropertyAnimation, menu_manage_open_dlg.Ui_MenuManageOpen) :

    def __init__ (self, parent=None) :
        '''Initialize and start up the UI'''

        super(MenuManageOpenCtrl, self).__init__(parent)

        #self.setWindowIcon(appicon)
        self.setupUi(self)
        self.connectionActions()


    def main (self) :
        '''This function shows the main dialog'''

        self.show()


    def connectionActions (self) :
        '''Connect to form buttons.'''

        self.pushButtonOk.clicked.connect(self.okClicked)


    def okClicked (self) :
        '''Execute the OK button.'''

        pid                     = self.lineEditPid.text().upper()

        saved_output = sys.stdout
        output_object = StringIO.StringIO()
        sys.stdout = output_object

#        if ProjDelete(pid).deleteProject(force) :
#            result = output_object.getvalue()
#            QMessageBox.information(self, "Project Open", result)
#        else :
#            result = output_object.getvalue()
#            QMessageBox.warning(self, "Project Open", result)

        # Output to terminal the stdout and close the dialog
        sys.stdout = saved_output
        self.close()


###############################################################################
############################## Dialog Starts Here #############################
###############################################################################

if __name__ == '__main__' :

    app = QApplication(sys.argv)
    window = MenuManageOpenCtrl()
    window.main()
    sys.exit(app.exec_())












