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
from rapuma.project.proj_setup          import ProjDelete

# Load GUI modules
from PySide                             import QtGui, QtCore
from PySide.QtGui                       import QDialog, QApplication, QMessageBox, QListWidgetItem
from PySide.QtCore                      import QPropertyAnimation
from rapuma.dialog                      import menu_project_remove_dlg

class MenuProjectRemoveCtrl (QDialog, QPropertyAnimation, menu_project_remove_dlg.Ui_MenuProjectRemove) :

    def __init__ (self, guiSettings, userConfig, parent=None) :
        '''Initialize and start up the UI'''

        super(MenuProjectRemoveCtrl, self).__init__(parent)

        # Setup the GUI
        self.setupUi(self)
        self.connectionActions()
        self.guiSettings            = guiSettings
        self.userConfig             = userConfig
        self.tools                  = Tools()
        self.removed                = None

        # Populate the list with projects
        for p in self.userConfig['Projects'].iteritems() :
            try :
                name = self.userConfig['Projects'][p[0]]['projectTitle']
            except :
                name = 'None'
            # The ID has the name tacked on
            self.listWidgetProjects.addItem(p[0] + ' (' + name + ')')
            self.listWidgetProjects.sortItems()


    def main (self) :
        '''This function shows the main dialog'''

        self.show()


    def connectionActions (self) :
        '''Connect to form buttons.'''

        self.pushButtonOk.clicked.connect(self.okClicked)


    def okClicked (self) :
        '''Execute the OK button.'''

        pid                     = self.listWidgetProjects.currentItem().text().split()[0]
        force                   = self.checkBoxBackup.isChecked()

        msgBox = QMessageBox()
#        msgBox.setTitle('Select Project')
        msgBox.setText("You have selected the " + pid + " project for removal.")
        if force :
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setInformativeText("A backup will be made.")
        else :
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setInformativeText("All data from this project will be deleted!")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec_()

        if ret == QtGui.QMessageBox.Ok :
            saved_output = sys.stdout
            output_object = StringIO.StringIO()
            sys.stdout = output_object

            if ProjDelete(pid).deleteProject(force) :
                # Clean up the userConfig settings here
                if pid == self.guiSettings.currentPid :
                    self.guiSettings.resetBookmarks()
                self.removed = True
                result = output_object.getvalue()
                QMessageBox.information(self, "Project Remove", result)
            else :
                result = output_object.getvalue()
                QMessageBox.warning(self, "Project Remove", result)

        # Close now regardless of whatever was clicked
        self.close()


###############################################################################
############################## Dialog Starts Here #############################
###############################################################################

if __name__ == '__main__' :

    app = QApplication(sys.argv)
    window = MenuProjectRemoveCtrl()
    window.main()
    sys.exit(app.exec_())












