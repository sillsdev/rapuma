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


# Load Rapuma modules
from rapuma.core.tools                  import Tools
from rapuma.core.user_config            import UserConfig
from rapuma.project.proj_setup          import ProjSetup

# Load GUI modules
from PySide                             import QtGui, QtCore
from PySide.QtGui                       import QDialog, QApplication, QMessageBox, QFileDialog
from PySide.QtCore                      import QPropertyAnimation
from rapuma.dialog                      import menu_project_add_dlg


class MenuProjectAddCtrl (QDialog, QPropertyAnimation, menu_project_add_dlg.Ui_MenuProjectAdd) :

    def __init__ (self, guiSettings, sysConfig, userConfig, parent=None) :
        '''Initialize and start up the UI'''

        super(MenuProjectAddCtrl, self).__init__(parent)

        # Grab some system info
        self.sysConfig                  = sysConfig
        self.guiSettings                = guiSettings
        self.systemVersion              = sysConfig['Rapuma']['systemVersion']
        # Setup the GUI
        self.setupUi(self)
        self.connectionActions()
        self.userConfig                 = userConfig
        # Set the default path for new project
        self.projDir                    = self.userConfig['Resources']['projects']
        self.lineEditProjPath.setText(self.projDir)
        self.completed                  = False


    def main (self) :
        '''This function shows the main dialog'''

        self.show()


    def connectionActions (self) :
        '''Connect to form buttons.'''

        self.pushButtonOk.clicked.connect(self.okClicked)
        self.pushButtonBrowse.clicked.connect(self.browseForFolder)


    def okClicked (self) :
        '''Execute the OK button.'''

        mediaType               = 'book'
        langCode                = self.lineEditLangId.text().upper()
        scriptCode              = self.lineEditScriptId.text().upper()
        projCode                = self.lineEditProjId.text().upper()
        pid                     = langCode + '-' + scriptCode + '-' + projCode
        projPath                = self.lineEditProjPath.text()
        projName                = self.lineEditProjName.text()
        projDescription         = self.textEditProjDescription.toPlainText()
        nProjPath               = os.path.join(projPath, pid)

# FIXME: A bunch of integrety checks need to go here to make sure
# the above data is good to go

        saved_output = sys.stdout
        output_object = StringIO.StringIO()
        sys.stdout = output_object

        if ProjSetup(pid).newProject(nProjPath, mediaType, projName, self.systemVersion, '') :
            result = output_object.getvalue()
            QMessageBox.information(self, "Project Add", result)
            self.guiSettings.currentPid = pid
            self.guiSettings.currentGid = ''
            self.guiSettings.currentCid = ''
            self.guiSettings.setBookmarks()
            self.completed = True
        else :
            result = output_object.getvalue()
            QMessageBox.warning(self, "Project Add", result)

        # Output to terminal the stdout and close the dialog
        sys.stdout = saved_output
        self.close()


    def browseForFolder (self) :
        '''Call a basic find file widget to get the folder we want to put this project in.'''

        dialog = QFileDialog(self, "Find a Folder")
        dialog.setDirectory(self.projDir)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly)
        if dialog.exec_() :
            # When the folder is found, change the right line edit box
            self.lineEditProjPath.setText(dialog.selectedFiles()[0])


###############################################################################
############################## Dialog Starts Here #############################
###############################################################################

if __name__ == '__main__' :

    app = QApplication(sys.argv)
    window = MenuProjectAddCtrl()
    window.main()
    sys.exit(app.exec_())












