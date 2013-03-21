#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project text tasks.

# History:
# 20120121 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil, codecs, re, subprocess
#from configobj import ConfigObj, Section

# Load the local classes
from rapuma.core.tools import *
from rapuma.project.manager import Manager
from rapuma.group.usfm import PT_Tools
from rapuma.core.proj_config import ConfigTools


###############################################################################
################################## Begin Class ################################
###############################################################################

class Text (Manager) :

    # Shared values
    xmlConfFile     = 'text.xml'

    def __init__(self, project, cfg, cType) :
        '''Do the primary initialization for this manager.'''

        super(Text, self).__init__(project, cfg)

        # Set values for this manager
        self.pt_tools               = PT_Tools(project)
        self.configTools            = ConfigTools(project)
        self.project                = project
        self.projConfig             = project.projConfig
        self.cfg                    = cfg
        self.cType                  = cType
        self.Ctype                  = cType.capitalize()
        self.gid                    = project.gid
        self.csid                   = project.projConfig['Groups'][self.gid]['csid']
        self.log                    = project.log
        self.manager                = self.cType + '_Text'
        self.managers               = project.managers
        self.rapumaXmlTextConfig    = os.path.join(self.project.local.rapumaConfigFolder, self.xmlConfFile)
        self.sourceEditor           = self.pt_tools.getSourceEditor(self.gid)
        self.setSourceEditor(self.sourceEditor)

        # File names
        grpPreprocValue             = self.projConfig['Groups'][self.gid]['preprocessScript']
        self.grpPreprocessFileName  = self.configTools.processLinePlaceholders(grpPreprocValue, grpPreprocValue)
        self.rpmPreprocessFileName  = self.grpPreprocessFileName.replace(self.gid, cType)
        # Folder paths
        self.rpmScriptsFolder       = os.path.join(project.local.rapumaScriptsFolder, self.cType)
        self.projComponentsFolder   = project.local.projComponentsFolder
        self.gidFolder              = os.path.join(self.projComponentsFolder, self.gid)
        # File names with paths
        self.grpPreprocessFile      = os.path.join(self.gidFolder, self.grpPreprocessFileName)
        self.rpmPreprocessFile      = os.path.join(self.rpmScriptsFolder, self.rpmPreprocessFileName)

        # Get persistant values from the config if there are any
        newSectionSettings = getPersistantSettings(self.project.projConfig['Managers'][self.manager], self.rapumaXmlTextConfig)
        if newSectionSettings != self.project.projConfig['Managers'][self.manager] :
            self.project.projConfig['Managers'][self.manager] = newSectionSettings
            writeConfFile(self.project.projConfig)

        self.compSettings = self.project.projConfig['Managers'][self.manager]

        for k, v in self.compSettings.iteritems() :
            setattr(self, k, v)


###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def setSourceEditor (self, editor) :
        '''Set the source editor for the cType. It assumes the editor is valid.
        This cannot fail.'''

        se = ''
        if testForSetting(self.project.projConfig['CompTypes'][self.Ctype], 'sourceEditor') :
            se = self.project.projConfig['CompTypes'][self.Ctype]['sourceEditor']

        if se != editor :
            self.project.projConfig['CompTypes'][self.Ctype]['sourceEditor'] = editor
            writeConfFile(self.project.projConfig)


    def updateManagerSettings (self, gid) :
        '''Update the settings for this manager if needed.'''

#        import pdb; pdb.set_trace()

        # If the source editor is PT, then a lot of information can be
        # gleaned from the .ssf file. Otherwise we will go pretty much with
        # the defaults and hope for the best.
        if self.sourceEditor.lower() == 'paratext' :
            # Do a compare on the settings
            ptSet = self.pt_tools.getPTSettings(self.gid)
            oldCompSet = self.compSettings.dict()
            # Don't overwrite manager settings (default sets reset to False) if
            # there already is a setting present on the nameFormID.
            if self.project.projConfig['Managers'][self.cType + '_Text']['nameFormID'] :
                newCompSet = self.pt_tools.mapPTTextSettings(self.compSettings.dict(), ptSet)
            else :
                newCompSet = self.pt_tools.mapPTTextSettings(self.compSettings.dict(), ptSet, True)

            if not newCompSet == oldCompSet :
                self.compSettings.merge(newCompSet)
                writeConfFile(self.project.projConfig)
                # Be sure to update the current session settings
                for k, v in self.compSettings.iteritems() :
                    setattr(self, k, v)
        # A generic editor means we really do not know where the text came
        # from. In that case, we just do the best we can.
        elif self.sourceEditor.lower() == 'generic' :
            if not self.project.projConfig['Managers'][self.cType + '_Text']['nameFormID'] or \
                not self.project.projConfig['Managers'][self.cType + '_Text']['postPart'] :
                self.project.projConfig['Managers'][self.cType + '_Text']['nameFormID'] = 'USFM'
                self.project.projConfig['Managers'][self.cType + '_Text']['postPart'] = 'usfm'

                writeConfFile(self.project.projConfig)
        else :
            self.project.log.writeToLog('TEXT-010', [self.sourceEditor])
            dieNow()

        return True


    def testCompTextFile (self, source, projSty = None) :
        '''This will direct a request to the proper validater for
        testing the source of a component text file.'''

        if self.cType == 'usfm' :
            # If this fails it will die at the validation process
            if self.project.components[cName].usfmTextFileIsValid(source, projSty) :
                self.project.log.writeToLog('TEXT-150', [source])
                return True
        else :
            self.project.log.writeToLog('TEXT-005', [self.cType])
            dieNow()


    def decodeText (self, fileName) :
        '''In case an encoding conversion is needed. This function will try
        to do that and if it fails, it should return a meaningful error msg.'''

        # First, test so see if we can even read the file
        try:
            fileObj = open(fileName, 'r').read()
        except Exception as e :
            terminal('decodeText() failed with the following error: ' + str(e))
            dieNow()
        # Now try to run the decode() function
        try:
            return fileObj.decode(self.sourceEncode)

        except Exception:
            terminal('decodeText() could not decode: [' + fileName + ']\n')
            dieNow()


###############################################################################
########################## Text Processing Functions ##########################
###############################################################################

    def turnOnOffPreprocess (self, gid, onOff) :
        '''Turn on or off preprocessing on incoming component text.'''

        self.projConfig['Groups'][gid]['usePreprocessScript'] = onOff.capitalize()
        writeConfFile(self.projConfig)
        self.log.writeToLog('PROC-140', [onOff, gid])


    def installPreprocess (self) :
        '''Check to see if a preprocess script is installed. If not, install the
        default script and give a warning that the script is not complete.'''

        # Check and copy if needed
        if not os.path.isfile(self.grpPreprocessFile) :
            shutil.copy(self.rpmPreprocessFile, self.grpPreprocessFile)
            makeExecutable(self.grpPreprocessFile)
            self.log.writeToLog('PROC-160')
            dieNow()
        else :
            self.log.writeToLog('PROC-165')


    def runProcessScript (self, target, scriptFile) :
        '''Run a text processing script on a component. This assumes the 
        component and the script are valid and the component lock is turned 
        off. If not, you cannot expect any good to come of this.'''

        # subprocess will fail if permissions are not set on the
        # script we want to run. The correct permission should have
        # been set when we did the installation.
        err = subprocess.call([scriptFile, target])
        if err == 0 :
            self.log.writeToLog('PROC-010', [fName(target), fName(scriptFile)])
        else :
            self.log.writeToLog('PROC-020', [fName(target), fName(scriptFile), str(err)])
            return False

        return True


    def scriptInstall (self, source, target) :
        '''Install a script. A script can be a collection of items in
        a zip file or a single .py script file.'''

        scriptTargetFolder, fileName = os.path.split(target)
        if isExecutable(source) :
            shutil.copy(source, target)
            makeExecutable(target)
        elif fName(source).split('.')[1].lower() == 'zip' :
            myZip = zipfile.ZipFile(source, 'r')
            for f in myZip.namelist() :
                data = myZip.read(f, source)
                # Pretty sure zip represents directory separator char as "/" regardless of OS
                myPath = os.path.join(scriptTargetFolder, f.split("/")[-1])
                try :
                    myFile = open(myPath, "wb")
                    myFile.write(data)
                    myFile.close()
                except :
                    pass
            myZip.close()
            return True
        else :
            dieNow('Script is an unrecognized type: ' + fName(source) + ' Cannot continue with installation.')


    def installPostProcess (self, cType, script, force = None) :
        '''Install a post process script into the main components processing
        folder for a specified component type. This script will be run on 
        every file of that type that is imported into the project. Some
        projects will have their own specially developed post process
        script. Use the "script" var to specify a process (which should be
        bundled in a system compatable way). If "script" is not specified
        we will copy in a default script that the user can modify. This is
        currently limited to Python scripts only which do in-place processes
        on the target files. The script needs to have the same name as the
        zip file it is bundled in, except the extention is .py instead of
        the bundle .zip extention.'''

        # Define some internal vars
        Ctype               = cType.capitalize()
        oldScript           = ''
        scriptName          = os.path.split(script)[1]
        scriptSourceFolder  = os.path.split(script)[0]
        scriptTarget        = os.path.join(self.local.projScriptsFolder, fName(script).split('.')[0] + '.py')
        if scriptName in self.projConfig['CompTypes'][Ctype]['postprocessScripts'] :
            oldScript = scriptName

        # First check for prexsisting script record
        if not force :
            if oldScript :
                self.log.writeToLog('POST-080', [oldScript])
                return False

        # In case this is a new project we may need to install a component
        # type and make a process (components) folder
        if not self.components[cType] :
            self.addComponentType(cType)

        # Make the target folder if needed
        if not os.path.isdir(self.local.projScriptsFolder) :
            os.makedirs(self.local.projScriptsFolder)

        # First check to see if there already is a script file, return if there is
        if os.path.isfile(scriptTarget) and not force :
            self.log.writeToLog('POST-082', [fName(scriptTarget)])
            return False

        # No script found, we can proceed
        if not os.path.isfile(scriptTarget) :
            self.scriptInstall(script, scriptTarget)
            if not os.path.isfile(scriptTarget) :
                dieNow('Failed to install script!: ' + fName(scriptTarget))
            self.log.writeToLog('POST-110', [fName(scriptTarget)])
        elif force :
            self.scriptInstall(script, scriptTarget)
            if not os.path.isfile(scriptTarget) :
                dieNow('Failed to install script!: ' + fName(scriptTarget))
            self.log.writeToLog('POST-115', [fName(scriptTarget)])

        # Record the script with the cType post process scripts list
        scriptList = self.projConfig['CompTypes'][Ctype]['postprocessScripts']
        if fName(scriptTarget) not in scriptList :
            self.projConfig['CompTypes'][Ctype]['postprocessScripts'] = addToList(scriptList, fName(scriptTarget))
            writeConfFile(self.projConfig)

        return True


    def removePostProcess (self, cType) :
        '''Remove (actually disconnect) a preprocess script from a

        component type. This will not actually remove the script. That
        would need to be done manually. Rather, this will remove the
        script name entry from the component type so the process cannot
        be accessed for this specific component type.'''

        Ctype = cType.capitalize()
        # Get old setting
        old = self.projConfig['CompTypes'][Ctype]['postprocessScripts']
        # Reset the field to ''
        if old != '' :
            self.projConfig['CompTypes'][Ctype]['postprocessScripts'] = ''
            writeConfFile(self.projConfig)
            self.log.writeToLog('POST-130', [old,Ctype])

        else :
            self.log.writeToLog('POST-135', [cType.capitalize()])

        return True


