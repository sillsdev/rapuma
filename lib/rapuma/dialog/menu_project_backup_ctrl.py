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


import os, sys, StringIO, datetime, shutil

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
        self.lineEditNewProjectLocation.setText(self.local.projHome)
        self.localPid               = self.guiSettings.currentPid
        self.curBakDict             = {}
        self.populateProjects()


    def populateProjects (self) :
        '''Populate the project combo box.'''

#        import pdb; pdb.set_trace()

        if self.comboBoxSelectProject.currentText() :
            self.localPid = self.comboBoxSelectProject.currentText()
        projects = self.userConfig['Projects'].keys()
        projects.sort()
        count = 0
        pSet = 0
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

        if self.comboBoxSelectProject.currentText() :
            self.localPid = self.comboBoxSelectProject.currentText()
        self.comboBoxSelectBackup.clear()
        self.curBakDict = {}
        bkups = os.listdir(os.path.join(self.local.userLibBackup, self.comboBoxSelectProject.currentText()))
        bkups.sort()
        for b in bkups :
            dt = b[:14]
            dt = datetime.datetime(int(dt[:4]), int(dt[4:6]), int(dt[6:8]), int(dt[8:10]), int(dt[10:12]), int(dt[12:14]))
            dt = dt.strftime('%A, %d-%b-%Y, %I:%M %p')
            # Because I don't know how to access multiple items in a comboBox index
            # I had to work around with the curBakDict thingy. This works but it
            # could be better if we could access multiple items in a single comboBox field
            self.comboBoxSelectBackup.addItem(dt)
            self.curBakDict[dt] = os.path.join(self.local.userLibBackup, self.comboBoxSelectProject.currentText(), b)


    def main (self) :
        '''This function shows the main dialog'''

        self.show()


    def connectionActions (self) :
        '''Connect to form buttons.'''

        self.pushButtonOk.clicked.connect(self.okClicked)
        self.comboBoxSelectProject.currentIndexChanged.connect(self.populateBackups)
        self.pushButtonBrowseAlternateBackupFile.clicked.connect(self.findAlternateBackup)
        self.pushButtonBrowseProjectLocation.clicked.connect(self.findProjPath)


    def findAlternateBackup (self) :
        '''Call a basic find file widget to get the file we want.'''

        dialog = QFileDialog(self, "Find a File")
        dialog.setDirectory(self.local.projHome)
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_() :
            # When the file is found, change the right line edit box
            self.lineEditAlternateBackup.setText(dialog.selectedFiles()[0])


    def findProjPath (self) :
        '''Call a basic find folder widget to get the path we want.'''

        dialog = QFileDialog(self, "Find a Folder")
        dialog.setDirectory(self.local.projHome)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly)
        if dialog.exec_() :
            # When the folder is found, change the right line edit box
            self.lineEditNewProjectLocation.setText(dialog.selectedFiles()[0])


    def okClicked (self) :
        '''Execute the OK button.'''

        actionContents = self.groupBoxBackupAction.layout()
        for i in range(0, actionContents.count()) :
            widget = actionContents.itemAt(i).widget()
            # Find the radio buttons
            if (widget!=0) and (type(widget) is QRadioButton) :

                # Backup current project
                if i == 0 and widget.isChecked() :
                    if ProjData(self.localPid).backupProject() :
                        QMessageBox.information(self, "Info", "<p>Project has been backed up.</p>")
                    else :
                        QMessageBox.warning(self, "Error!", "<p>Project was not backed up. Please check the logs for the reason.</p>")

                # Restore selected backup, to selected project
                elif i == 1 and widget.isChecked() :
                    # If there is an exsiting project make a temp backup in 
                    # case something goes dreadfully wrong
                    if os.path.exists(self.local.projHome) :
                        self.tools.makeFolderBackup(self.local.projHome)
                    if ProjData(self.localPid).backupRestore(self.curBakDict[self.comboBoxSelectBackup.currentText()]) :
                        QMessageBox.information(self, "Info", "<p>Project has been restored.")
                    else :
                        QMessageBox.warning(self, "Error!", "<p>Project was not restored. Please check the logs for the reason.")

                # Remove Selected Backup
                elif i == 2 and widget.isChecked() :
                    # Give a warning
                    msg = QtCore.QT_TR_NOOP("<p>Are you sure you want to delete the backup made on:</p>" \
                            "<p>" + self.comboBoxSelectBackup.currentText() + "</p>" \
                            "<p>This data will be permanently removed from your system.</p>")
                    reply = QMessageBox.critical(self, "Warning", msg, QMessageBox.StandardButton.Ok | QMessageBox.Cancel)
                    if reply == QMessageBox.StandardButton.Ok :
                        if os.path.exists(self.curBakDict[self.comboBoxSelectBackup.currentText()]) :
                            if not os.remove(self.curBakDict[self.comboBoxSelectBackup.currentText()]) :
                                QMessageBox.information(self, "Info", "<p>The backup created on:</p>" \
                                    "<p>" + self.comboBoxSelectBackup.currentText() + "</p>" \
                                    "<p>has been removed.</p>")

                # Restore Alternate Backup
                elif i == 3 and widget.isChecked() :
                    # Check for data
                    if not os.path.isfile(self.lineEditAlternateBackup.text()) :
                        QMessageBox.warning(self, "Error!", "<p>A valid path has not been entered in the Alternate Backup File field.")
                    else :
                        # Give a final warning
                        msg = QtCore.QT_TR_NOOP("<p>You are about to overwrite this project with new data:</p>" \
                                "<p>" + self.localPid + "</p>" \
                                "<p>Any data in the current copy of the project will be lost.</p>")
                        reply = QMessageBox.critical(self, "Warning", msg, QMessageBox.StandardButton.Ok | QMessageBox.Cancel)
                        if reply == QMessageBox.StandardButton.Ok :
                            if ProjData(self.localPid).backupRestore(self.lineEditAlternateBackup.text()) :
                                QMessageBox.information(self, "Info", "<p>Project has been restored from the alternate backup file.")
                            else :
                                QMessageBox.warning(self, "Error!", "<p>Project was not restored. Please check the logs for the reason.")

                # New Project from Alternate
                elif i == 4 and widget.isChecked() :
                    # Check for project and field data
                    if not os.path.isfile(self.lineEditAlternateBackup.text()) :
                        QMessageBox.warning(self, "Error!", "<p>A valid path/file has not been entered in the Alternate Backup File field.")
                    elif not os.path.isdir(self.lineEditNewProjectLocation.text()) :
                        QMessageBox.warning(self, "Error!", "<p>A valid path/folder has not been entered in the New Project folder field.")
                    else :
                        # First we need to find out what the real PID of the backup is
                        thisPid = self.tools.discoverPidFromZip(self.lineEditAlternateBackup.text())
                        # Check to see if the PID we found is already registered in the system
                        if thisPid != '' and not self.userConfig['Projects'].has_key(thisPid) :
                            # If not, do the restore
                            if ProjData(thisPid).restoreExternalBackup(self.lineEditAlternateBackup.text(), self.lineEditNewProjectLocation.text()) :
                                QMessageBox.information(self, "Info", "<p>The new/restored project has been added to your local system.")
                                self.localPid = thisPid
                            else :
                                QMessageBox.warning(self, "Error!", "<p>Failed to create new/restored project. Please check the logs for the reason.")
                        else :
                            QMessageBox.warning(self, "Error!", "<p>The project [" + thisPid + "] already exists. It must be removed before this operation can be done.")

                # Flush Project Backups
                elif i == 5 and widget.isChecked() :
                    # Check for data
# FIXME: Working here

                    msg = QtCore.QT_TR_NOOP("<p>You are about to delete all the backup data for this project:</p>" \
                            "<p>" + self.localPid + "</p>" \
                            "<p>This might be a really bad idea so choose wisely.</p>")
                    reply = QMessageBox.critical(self, "Warning", msg, QMessageBox.StandardButton.Ok | QMessageBox.Cancel)
                    if reply == QMessageBox.StandardButton.Ok :
                        killDir = os.path.join(self.local.userLibBackup, self.localPid)
                        
                        # Need to get rid of all the files but not the folder
                        
                        if os.path.isdir(killDir) :
                            if shutil.rmtree(killDir) :
                                print 'killed it'
                            else :
                                print 'saved it'
                        else :
                            print 'not there'


#            elif cmdType == 'backup' :
#                if not sourcePath and uc.userConfig['Projects'].has_key(pid) :
#                    ProjData(pid).restoreLocalBackup(args.bak_num)
#                else :
#                    if sourcePath :
#                        ProjData(pid).restoreExternalBackup(sourcePath, targetPath)
#                    else :
#                        sys.exit('\nERROR: To restore this backup, a path must be provided with -t. Process halting.\n')


#        self.close()


###############################################################################
############################## Dialog Starts Here #############################
###############################################################################

if __name__ == '__main__' :

    app = QApplication(sys.argv)
    window = MenuProjectBackupCtrl()
    window.main()
    sys.exit(app.exec_())












