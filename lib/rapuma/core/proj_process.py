#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project data processing operations.

###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, shutil, subprocess, zipfile, StringIO
from configobj                      import ConfigObj

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog
#from rapuma.core.paratext           import Paratext
from rapuma.project.proj_config     import Config


class ProjProcess (object) :

    def __init__(self, pid, gid = None, projectConfig = None) :
        '''Intitate the whole class and create the object.'''

        self.pid                    = pid
        self.tools                  = Tools()
        self.user                   = UserConfig()
        self.userConfig             = self.user.userConfig
        if projectConfig :
            self.projectConfig      = projectConfig
        else :
            self.proj_config            = Config(self.pid)
            self.proj_config.getProjectConfig()
            self.projectConfig          = self.proj_config.projectConfig
        self.local                  = ProjLocal(pid, gid, self.projectConfig)
        self.log                    = ProjLog(pid)
        self.paratext               = Paratext(pid, gid)

        # Log messages for this module
        self.errorCodes     = {
            '0000' : ['MSG', 'Placeholder message'],
            'XPRT-000' : ['MSG', 'Messages for export issues (probably only in project.py)'],
            'XPRT-005' : ['MSG', 'Unassigned error message ID.'],
            'XPRT-010' : ['ERR', 'Export file name could not be formed with available configuration information.'],
            'XPRT-020' : ['ERR', 'Unable to export: [<<1>>].'],
            'XPRT-030' : ['MSG', 'Files exported to [<<1>>].'],
            'XPRT-040' : ['MSG', 'Beginning export, please wait...'],
            'XPRT-050' : ['MSG', 'Unassigned error message ID.'],

            '1210' : ['MSG', 'Processes completed successfully on: [<<1>>] by [<<2>>]'],
            '1220' : ['ERR', 'Processes for [<<1>>] failed. Script [<<2>>] returned this error: [<<3>>]'],
            '1240' : ['MSG', 'Component group preprocessing [<<1>>] for group [<<2>>].'],
            '1260' : ['ERR', 'Installed the default component preprocessing script. Editing will be required for it to work with your project.'],
            '1265' : ['LOG', 'Component preprocessing script is already installed.'],

        }


###############################################################################
############################### Export Functions ##############################
###############################################################################
####################### Error Code Block Series = 0200 ########################
###############################################################################

# FIXME: This needs to be rewritten

    #def export (self, cType, cName, path = None, script = None, bundle = False, force = False) :
        #'''Facilitate the exporting of project text. It is assumed that the
        #text is clean and ready to go and if any extraneous publishing info
        #has been injected into the text, it will be removed by an appropreate
        #post-process that can be applied by this function. No validation
        #will be initiated by this function.'''
        
        ## FIXME - Todo: add post processing script feature

        ## Probably need to create the component object now
        #self.createComponent(cName)

        ## Figure out target path
        #if path :
            #path = self.tools.resolvePath(path)
        #else :
            #parentFolder = os.path.dirname(self.local.projHome)
            #path = os.path.join(parentFolder, 'Export')

        ## Make target folder if needed
        #if not os.path.isdir(path) :
            #os.makedirs(path)

        ## Start a list for one or more files we will process
        #fList = []

        ## Will need the stylesheet for copy
        #projSty = self.projectConfig['Managers'][cType + '_Style']['mainStyleFile']
        #projSty = os.path.join(self.local.projStyleFolder, projSty)
        ## Process as list of components

        #self.log.writeToLog('XPRT-040')
        #for cid in self.components[cName].getSubcomponentList(cName) :
            #cidCName = self.components[cName].getRapumaCName(cid)
            #ptName = PT_Tools(self).formPTName(cName, cid)
            ## Test, no name = no success
            #if not ptName :
                #self.log.writeToLog('XPRT-010')
                #self.tools.dieNow()

            #target = os.path.join(path, ptName)
            #source = os.path.join(self.local.projComponentFolder, cidCName, cid + '.' + cType)
            ## If shutil.copy() spits anything back its bad news
            #if shutil.copy(source, target) :
                #self.log.writeToLog('XPRT-020', [self.tools.fName(target)])
            #else :
                #fList.append(target)

        ## Start the main process here
        #if bundle :
            #archFile = os.path.join(path, cName + '_' + self.tools.ymd() + '.zip')
            ## Hopefully, this is a one time operation but if force is not True,
            ## we will expand the file name so nothing is lost.
            #if not force :
                #if os.path.isfile(archFile) :
                    #archFile = os.path.join(path, cName + '_' + self.tools.fullFileTimeStamp() + '.zip')

            #myzip = zipfile.ZipFile(archFile, 'w', zipfile.ZIP_DEFLATED)
            #for f in fList :
                ## Create a string object from the contents of the file
                #strObj = StringIO.StringIO()
                #for l in open(f, "rb") :
                    #strObj.write(l)
                ## Write out string object to zip
                #myzip.writestr(self.tools.fName(f), strObj.getvalue())
                #strObj.close()
            ## Close out the zip and report
            #myzip.close()
            ## Clean out the folder
            #for f in fList :
                #os.remove(f)
            #self.log.writeToLog('XPRT-030', [self.tools.fName(archFile)])
        #else :
            #self.log.writeToLog('XPRT-030', [path])

        #return True


###############################################################################
########################## Text Processing Functions ##########################
###############################################################################
######################## Error Code Block Series = 1200 #######################
###############################################################################

    def turnOnOffPreprocess (self, gid, onOff) :
        '''Turn on or off preprocessing on incoming component text.'''

        self.projectConfig['Groups'][gid]['usePreprocessScript'] = onOff
        self.tools.writeConfFile(self.projectConfig)
        self.log.writeToLog(self.errorCodes['1240'], [str(onOff), gid])


    def checkForPreprocessScript (self, gid) :
        '''Check to see if a preprocess script is installed. If not, install the
        default script and give a warning that the script is not complete.'''

        # First make sure the Scripts folder is there
        if not os.path.isdir(self.local.projScriptFolder) :
            os.makedirs(self.local.projScriptFolder)

        # Check and copy if needed
        if not os.path.isfile(self.local.groupPreprocessFile) :
            shutil.copy(self.local.rpmPreprocessFile, self.local.groupPreprocessFile)
            self.tools.makeExecutable(self.local.groupPreprocessFile)
            self.log.writeToLog(self.errorCodes['1260'])
        else :
            self.log.writeToLog(self.errorCodes['1265'])


    def runProcessScript (self, target, scriptFile) :
        '''Run a text processing script on a component. This assumes the 
        component and the script are valid and the component lock is turned 
        off. If not, you cannot expect any good to come of this.'''

        # subprocess will fail if permissions are not set on the
        # script we want to run. The correct permission should have
        # been set when we did the installation.
        err = subprocess.call([scriptFile, target])
        if err == 0 :
            self.log.writeToLog(self.errorCodes['1210'], [self.tools.fName(target), self.tools.fName(scriptFile)])
        else :
            self.log.writeToLog(self.errorCodes['1220'], [self.tools.fName(target), self.tools.fName(scriptFile), str(err)])
            return False

        return True


    def scriptInstall (self, source, target) :
        '''Install a script. A script can be a collection of items in
        a zip file or a single .py script file.'''

        scriptTargetFolder, fileName = os.path.split(target)
        if self.tools.isExecutable(source) :
            shutil.copy(source, target)
            self.tools.makeExecutable(target)
        elif self.tools.fName(source).split('.')[1].lower() == 'zip' :
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
            self.tools.dieNow('Script is an unrecognized type: ' + self.tools.fName(source) + ' Cannot continue with installation.')


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
        scriptTarget        = os.path.join(self.local.projScriptFolder, self.tools.fName(script).split('.')[0] + '.py')
        if scriptName in self.projectConfig['CompTypes'][Ctype]['postprocessScripts'] :
            oldScript = scriptName

        # First check for prexsisting script record
        if not force :
            if oldScript :
                self.log.writeToLog('POST-080', [oldScript])
                return False

        # In case this is a new project we may need to install a component
        # type and make a process (components) folder
        if not self.components[cType] :
            self.tools.addComponentType(self.projectConfig, self.local, cType)

        # Make the target folder if needed
        if not os.path.isdir(self.local.projScriptFolder) :
            os.makedirs(self.local.projScriptFolder)

        # First check to see if there already is a script file, return if there is
        if os.path.isfile(scriptTarget) and not force :
            self.log.writeToLog('POST-082', [self.tools.fName(scriptTarget)])
            return False

        # No script found, we can proceed
        if not os.path.isfile(scriptTarget) :
            self.scriptInstall(script, scriptTarget)
            if not os.path.isfile(scriptTarget) :
                self.tools.dieNow('Failed to install script!: ' + self.tools.fName(scriptTarget))
            self.log.writeToLog('POST-110', [self.tools.fName(scriptTarget)])
        elif force :
            self.scriptInstall(script, scriptTarget)
            if not os.path.isfile(scriptTarget) :
                self.tools.dieNow('Failed to install script!: ' + self.tools.fName(scriptTarget))
            self.log.writeToLog('POST-115', [self.tools.fName(scriptTarget)])

        # Record the script with the cType post process scripts list
        scriptList = self.projectConfig['CompTypes'][Ctype]['postprocessScripts']
        if self.tools.fName(scriptTarget) not in scriptList :
            self.projectConfig['CompTypes'][Ctype]['postprocessScripts'] = self.tools.addToList(scriptList, self.tools.fName(scriptTarget))
            self.tools.writeConfFile(self.projectConfig)

        return True


    def removePostProcess (self, cType) :
        '''Remove (actually disconnect) a preprocess script from a

        component type. This will not actually remove the script. That
        would need to be done manually. Rather, this will remove the
        script name entry from the component type so the process cannot
        be accessed for this specific component type.'''

        Ctype = cType.capitalize()
        # Get old setting
        old = self.projectConfig['CompTypes'][Ctype]['postprocessScripts']
        # Reset the field to ''
        if old != '' :
            self.projectConfig['CompTypes'][Ctype]['postprocessScripts'] = ''
            self.tools.writeConfFile(self.projectConfig)
            self.log.writeToLog('POST-130', [old,Ctype])

        else :
            self.log.writeToLog('POST-135', [cType.capitalize()])

        return True




