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


import os, sys, StringIO, datetime

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
from rapuma.dialog                      import menu_project_backup_dlg

class MenuProjectBackupCtrl (QDialog, QPropertyAnimation, menu_project_backup_dlg.Ui_MenuProjectBackup) :

    def __init__ (self, guiSettings, userConfig, parent=None) :
        '''Initialize and start up the UI'''

        super(MenuProjectBackupCtrl, self).__init__(parent)

        # Setup the GUI
        self.setupUi(self)
        self.connectionActions()
        self.completed              = False
        self.tools                  = Tools()
        self.guiSettings            = guiSettings
        self.userConfig             = userConfig
        self.local                  = ProjLocal(self.guiSettings.currentPid)
        self.lineEditProjectLocation.setText(self.local.projHome)
        self.localPid               = self.guiSettings.currentPid
        self.populateProjects()


    def populateProjects (self) :
        '''Populate the project combo box.'''

#        import pdb; pdb.set_trace()

        if self.comboBoxSelectProject.currentText() :
            self.localPid = self.comboBoxSelectProject.currentText()
        projects = self.userConfig['Projects'].keys()
        projects.sort()
        count = 0
        pSet = ''
        for proj in projects :
            if proj == self.localPid :
                pSet = count
            count +=1
        self.comboBoxSelectProject.clear()
        self.comboBoxSelectProject.addItems(projects)
        self.comboBoxSelectProject.setCurrentIndex(pSet)
        self.populateBackups()


    def populateBackups (self) :
        '''Populate the backup combo box.'''

        self.comboBoxSelectBackup.clear()
        bkups = os.listdir(os.path.join(self.local.userLibBackup, self.comboBoxSelectProject.currentText()))
        bkups.sort()
        for b in bkups :
            dt = b[:14]
            bn = dt
            dt = datetime.datetime(int(dt[:4]), int(dt[4:6]), int(dt[6:8]), int(dt[8:10]), int(dt[10:12]), int(dt[12:14]))
            dt = dt.strftime('%A, %d-%b-%Y, %I:%M %p')
            self.comboBoxSelectBackup.addItem(dt, bn)


    def main (self) :
        '''This function shows the main dialog'''

        self.show()


    def connectionActions (self) :
        '''Connect to form buttons.'''

        self.pushButtonOk.clicked.connect(self.okClicked)
        self.comboBoxSelectProject.currentIndexChanged.connect(self.populateBackups)


    def okClicked (self) :
        '''Execute the OK button.'''

        # Look at the radio buttons in the Action group
        # (This was taken from: 
        #   http://stackoverflow.com/questions/2089897/finding-checked-qradiobutton-among-many-into-a-qvboxlayout )
        actionContents = self.groupBoxBackupAction.layout()
        for i in range(0, actionContents.count()) :
            widget = actionContents.itemAt(i).widget()
            # Find the radio buttons
            if (widget!=0) and (type(widget) is QRadioButton) :
                # Do an action according to wich one was selected
                if i == 0 and widget.isChecked() :
                    print 'Backup Selected', i, self.comboBoxSelectBackup.itemData(1)



                    
# FIXME: Something is not quite right here with this command
                    
                    ProjData(self.localPid).restoreLocalBackup(self.comboBoxSelectBackup.itemData(1))




                elif i == 1 and widget.isChecked() :
                    print 'Remove Backup', i
                elif i == 2 and widget.isChecked() :
                    print 'Restore as new', i
                elif i == 3 and widget.isChecked() :
                    print 'Restore as new', i

#            elif cmdType == 'backup' :
#                if not sourcePath and uc.userConfig['Projects'].has_key(pid) :
#                    ProjData(pid).restoreLocalBackup(args.bak_num)
#                else :
#                    if sourcePath :
#                        ProjData(pid).restoreExternalBackup(sourcePath, targetPath)
#                    else :
#                        sys.exit('\nERROR: To restore this backup, a path must be provided with -t. Process halting.\n')


        self.close()


###############################################################################
############################## Dialog Starts Here #############################
###############################################################################

if __name__ == '__main__' :

    app = QApplication(sys.argv)
    window = MenuProjectBackupCtrl()
    window.main()
    sys.exit(app.exec_())












