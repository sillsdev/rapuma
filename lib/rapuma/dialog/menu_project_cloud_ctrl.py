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
from rapuma.dialog                      import menu_project_cloud_dlg

class MenuProjectCloudCtrl (QDialog, QPropertyAnimation, menu_project_cloud_dlg.Ui_MenuProjectCloud) :

    def __init__ (self, pid, userConfig, parent=None) :
        '''Initialize and start up the UI'''

        super(MenuProjectCloudCtrl, self).__init__(parent)

        # Setup the GUI
        self.setupUi(self)
        self.connectionActions()
        self.pid                    = pid
        self.userConfig             = userConfig
        self.lineEditProjectLocal.setText(self.userConfig['Projects'][self.pid]['projectPath'])
        self.lineEditProjectCloud.setText(self.userConfig['Resources']['cloud'])


    def main (self) :
        '''This function shows the main dialog'''

        self.show()


    def connectionActions (self) :
        '''Connect to form buttons.'''

        self.pushButtonOk.clicked.connect(self.okClicked)


    def okClicked (self) :
        '''Execute the OK button.'''

        flush                   = self.checkBoxFlush.isChecked()
        backup                  = self.checkBoxBackup.isChecked()

        # Look at the radio buttons in the Action group
        # (This was taken from: 
        #   http://stackoverflow.com/questions/2089897/finding-checked-qradiobutton-among-many-into-a-qvboxlayout )
        actionContents = self.groupBoxAction.layout()
        for i in range(0, actionContents.count()) :
            widget = actionContents.itemAt(i).widget()
            # Find the radio buttons
            if (widget!=0) and (type(widget) is QtGui.QRadioButton) :
                # Do an action according to wich one was selected
                if i == 0 and widget.isChecked() :
                    print 'Pushing to cloud'
                elif i == 1 and widget.isChecked() :
                    print 'Pulling from cloud'
                elif i == 2 and widget.isChecked() :
                    print 'Restoring from cloud'

# These are the basic things we want to do
#ProjData(pid).pullFromCloud(args.force, targetPath)
#ProjData(pid).backupProject(targetPath)
#ProjData(pid).pushToCloud(args.force)



        self.close()


###############################################################################
############################## Dialog Starts Here #############################
###############################################################################

if __name__ == '__main__' :

    app = QApplication(sys.argv)
    window = MenuProjectCloudCtrl()
    window.main()
    sys.exit(app.exec_())












