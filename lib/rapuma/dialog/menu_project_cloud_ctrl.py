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
from rapuma.core.proj_data              import ProjData
from rapuma.core.proj_local             import ProjLocal

# Load GUI modules
from PySide                             import QtGui, QtCore
from PySide.QtGui                       import QDialog, QApplication, QMessageBox, \
                                                QListWidgetItem, QFileDialog, \
                                                 QRadioButton
from PySide.QtCore                      import QPropertyAnimation
from rapuma.dialog                      import menu_project_cloud_dlg

class MenuProjectCloudCtrl (QDialog, QPropertyAnimation, menu_project_cloud_dlg.Ui_MenuProjectCloud) :

    def __init__ (self, guiSettings, userConfig, parent=None) :
        '''Initialize and start up the UI'''

        super(MenuProjectCloudCtrl, self).__init__(parent)

        # Setup the GUI
        self.setupUi(self)
        self.connectionActions()
        self.completed              = False
        self.tools                  = Tools()
        self.guiSettings            = guiSettings
        self.userConfig             = userConfig
        self.local                  = ProjLocal(self.guiSettings.currentPid)
        self.lineEditProjectLocal.setText(self.local.projHome)
        self.populateProjects()


    def populateProjects (self) :
        '''Populate the combo box list.'''

        dirs = os.listdir(self.local.userCloudStorage)
        dirs.sort()
        for d in dirs :
            self.comboBoxCloudProjects.addItem(d)


    def main (self) :
        '''This function shows the main dialog'''

        self.show()


    def connectionActions (self) :
        '''Connect to form buttons.'''

        self.pushButtonOk.clicked.connect(self.okClicked)
        self.pushButtonLocalBrowse.clicked.connect(self.findProjPath)


    def findProjPath (self) :
        '''Call a basic find folder widget to get the path we want.'''

        dialog = QFileDialog(self, "Find a Folder")
        dialog.setDirectory(self.local.projHome)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly)
        if dialog.exec_() :
            # When the folder is found, change the right line edit box
            self.lineEditProjectLocal.setText(dialog.selectedFiles()[0])


    def okClicked (self) :
        '''Execute the OK button.'''

        # Look at the radio buttons in the Action group
        # (This was taken from: 
        #   http://stackoverflow.com/questions/2089897/finding-checked-qradiobutton-among-many-into-a-qvboxlayout )
        actionContents = self.groupBoxAction.layout()
        for i in range(0, actionContents.count()) :
            widget = actionContents.itemAt(i).widget()
            # Find the radio buttons
            if (widget!=0) and (type(widget) is QRadioButton) :
                # Do an action according to wich one was selected
                if i == 0 and widget.isChecked() :
                    ProjData(self.guiSettings.currentPid).pushToCloud(self.checkBoxFlush.isChecked())
                elif i == 2 and widget.isChecked() :
                    ProjData(self.guiSettings.currentPid).pullFromCloud(self.checkBoxBackup.isChecked(), self.lineEditProjectLocal.text())
                elif i == 4 and widget.isChecked() :
                    if os.path.exists(os.path.join(self.local.userCloudStorage, self.comboBoxCloudProjects.currentText())) :
                        self.guiSettings.currentPid = self.comboBoxCloudProjects.currentText()
                        self.guiSettings.currentGid = ''
                        self.guiSettings.currentCid = ''
                        self.guiSettings.setBookmarks()
                        ProjData(self.guiSettings.currentPid).pullFromCloud(False, self.lineEditProjectLocal.text())
                        self.completed = True
                    else :
                        QMessageBox.warning(self, "Error!", """<p>Cloud ID not valid.""")


        self.close()


###############################################################################
############################## Dialog Starts Here #############################
###############################################################################

if __name__ == '__main__' :

    app = QApplication(sys.argv)
    window = MenuProjectCloudCtrl()
    window.main()
    sys.exit(app.exec_())












