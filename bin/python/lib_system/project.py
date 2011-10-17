#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project infrastructure tasks.

# History:
# 20110823 - djd - Started with intial file from RPM project


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys, fileinput, shutil, imp
#from configobj import ConfigObj, Section


# Load the local classes
from tools import *
import component
import auxiliary

###############################################################################
################################## Begin Class ################################
###############################################################################

class Project (object) :

    def __init__(self, projConfig, userConfig, projHome, userHome, rpmHome) :

        self.projHome           = projHome
        self.userHome           = userHome
        self.rpmHome            = rpmHome

        # Load project config files
        self._projConfig        = projConfig
        self._userConfig        = userConfig
        self._components        = {}
        self._auxilaries        = {}

        # Set all the initial paths and locations
        # System level paths
        self.rpmHome           = rpmHome
        self.userHome          = userHome
        self.projHome          = projHome
        self.rpmAuxTypes       = os.path.join(rpmHome, 'resources', 'lib_auxiliaryTypes')
        self.rpmCompTypes      = os.path.join(rpmHome, 'resources', 'lib_compTypes')
        self.rpmProjTypes      = os.path.join(rpmHome, 'resources', 'lib_projTypes')
        self.rpmShare          = os.path.join(rpmHome, 'resources', 'lib_share')
        self.rpmFonts          = os.path.join(rpmHome, 'resources', 'lib_share', 'Fonts')
        # User/Global level paths
        self.userScripts        = os.path.join(userHome, 'resources', 'lib_scripts')
        self.userFonts          = os.path.join(userHome, 'resources', 'lib_share', 'Fonts')
        self.userIllustrations  = os.path.join(userHome, 'resources', 'lib_illustratons')
        self.userAdmin          = os.path.join(userHome, 'resources', 'lib_admin')
        self.userCompTypes      = os.path.join(userHome, 'resources', 'lib_compTypes')
        self.userProjTypes      = os.path.join(userHome, 'resources', 'lib_projTypes')

        # Set all the system settings
        if self._userConfig :
            self.projConfFile   = os.path.join(self.projHome, '.project.conf')
            self.userConfFile   = os.path.join(self.userHome, 'rpm.conf')
            for k in ('systemVersion',      'userName',
                      'debugging',          'lastEditDate',
                      'projLogLineLimit',   'lockExt') :
                setattr(self, k, self._userConfig['System'][k] if self._userConfig else None)

            self.orgLastEditDate    = self.lastEditDate

        # Load the project vars if this is a valid project
        if len(self._projConfig) :
            for k in (  'projectType',                  'projectName',
                        'projectIDCode',                'validCompTypes',
                        'validAuxTypes',                'projectComponentBindingOrder') :
                 setattr(self, k, self._projConfig['ProjectInfo'][k] if self._projConfig else None)
            # Log file names
            for k in (  'projLogFile',                  'projErrorLogFile') :
                 setattr(self, k, self._userConfig['Files'][k]['name'] if self._projConfig else None)

        # Set some flags
        self.writeOutProjConfFile   = False
        self.writeOutUserConfFile   = False
        self.isProjectInitalized    = False

        # If this project is still new these may not exist yet
        try :
            # Set init flag on all comp types to False
            if self._projConfig['ComponentTypes'] :
                for key in self._projConfig['ComponentTypes'].keys() :
                    setattr(self, key + 'Initialized', False)

            # Set init flag on all comps to False
            if self._projConfig['Components'] :
                for key in self._projConfig['Components'].keys() :
                    setattr(self, key + 'Initialized', False)

            # Walk the ComponentTypes section and try to load commands if there are any
            for comp in self._projConfig['ComponentTypes'].keys() :
                sys.path.insert(0, os.path.join(self.rpmCompTypes, comp, 'lib_python'))
                __import__(comp)
                __import__(comp + '_command')
            
            # Walk the AuxiliaryTypes section and try to load commands if there are any
            for aux in self._projConfig['AuxiliaryTypes'].keys() :
                sys.path.insert(0, os.path.join(self.rpmAuxTypes, aux, 'lib_python'))
                __import__(aux)
                __import__(aux + '_command')
            
                # Clean up the path, we don't need this stuck there
                del sys.path[0]
 
        except :
            pass

        
 
###############################################################################
############################ Project Level Functions ##########################
###############################################################################


    def makeProject (self, ptype, pname, pid, pdir='') :
        '''Create a new publishing project.'''

        # Run some basic tests to see if this project can be created
        # Grab the cwd if pdir is empty for the default
        if not pdir or pdir == '.' :
            pdir = os.getcwd()

        # So now that we have a pdir it needs testing
        pdir = os.path.abspath(pdir)
        # Test for parent project.
        if os.path.isfile(os.path.join(pdir, '.project.conf')) :
            self.writeToLog('ERR', 'Halt! Live project already defined in this location')
            return False
        elif os.path.isfile(os.path.join(pdir, '.project.conf' + self.lockExt)) :
            self.writeToLog('ERR', 'Halt! Locked project already defined in target folder')
            return False
        elif os.path.isfile(os.path.join(os.path.dirname(pdir), '.project.conf')) :
            self.writeToLog('ERR', 'Halt! Live project already defined in parent folder')
            return False
        elif os.path.isfile(os.path.join(os.path.dirname(pdir), '.project.conf' + self.lockExt)) :
            self.writeToLog('ERR', 'Halt! Locked project already defined in parent folder')
            return False
        elif not os.path.isdir(os.path.dirname(pdir)) :
            self.writeToLog('ERR', 'Halt! Not a valid (parent) path: ' + pdir)
            return False

        # Test if this project already exists in the user's config file.
        if isRecordedProject(self.userConfFile, pid) :
            self.writeToLog('ERR', 'Halt! ID [' + pid + '] already defined for another project')
            return False

        # If we made it to this point we need to check to see if the project
        # folder exists, if it doesn't make.  We can create only one level deep
        # though.'
        if not os.path.isdir(pdir) :
            os.mkdir(pdir)

        # Create a new version of the project config file
        newProjConfig = getProjSettings(self.userHome, self.rpmHome, ptype)
        self.writeOutProjConfFile = True
        self._projConfig = newProjConfig
        # We will do the project init when the first component is processed

        # Create intitial project settings
        date = tStamp()
        self._projConfig['ProjectInfo']['projectType']            = ptype
        self._projConfig['ProjectInfo']['projectName']            = pname
        self._projConfig['ProjectInfo']['projectLastEditDate']    = ''
        self._projConfig['ProjectInfo']['projectCreateDate']      = date
        self._projConfig['ProjectInfo']['projectIDCode']          = pid
        recordProject(self.userConfFile, self._projConfig, pdir)
        
        # Set some vars that will be needed
        self.projLogFile        = self._userConfig['Files']['projLogFile']['name']
        self.projErrorLogFile   = self._userConfig['Files']['projErrorLogFile']['name']

        # Finally write out the project config file
        writeProjConfFile(self._projConfig, pdir)
        self.writeOutProjConfFile = False
        self.writeToLog('MSG', 'Created [' + pid + '] project at: ' + date, 'project.makeProject()')


    def removeProject (self, pid='') :
        '''Remove the project from the RPM system.  This will not remove the
        project data but will 'disable' the project.'''

        # If no pid was given we'll try to get the current on if there is one
        if pid == '' :
            if self.projectIDCode :
                pid = self.projectIDCode
            else :
                terminal('Project ID code not given or found. Remove project failed.')
                return False

        # If we made it this far we should be able to remove it
        try :
            # Check to see if the project does exist in the user config
            if self._userConfig['Projects'][pid] :
                projPath = self._userConfig['Projects'][pid]['projectPath']
                projConfFile = os.path.join(projPath, '.project.conf')
                # Disable the project
                if os.path.isfile(projConfFile) :
                    os.rename(projConfFile, projConfFile + self.lockExt)

                # Remove references from user rpm.conf
                del self._userConfig['Projects'][pid]
                reportSysConfUpdate(self)

                # Report the process is done
                self.writeToLog('MSG', 'Project [' + pid + '] removed from system configuration.')
                return True

        except :
            terminal('Project ID [' + pid + '] not found in system configuration.')
            return False


    def restoreProject (self, pdir='') :
        '''Restore a project in the current folder'''

        # Normalize the path to the project we want to restore
        if pdir == '' or pdir == '.' :
            pdir = os.getcwd()
        else :
            pdir = os.path.abspath(pdir)

        # Restore the project
        projConfFile = os.path.join(pdir, '.project.conf')
        if os.path.isfile(projConfFile + self.lockExt) :
            os.rename(projConfFile + self.lockExt, projConfFile)
            
            # We could put a lot of code here to get this project recorded and
            # check the integrity, or, we could just let that happen the next
            # time RPM is run on the project.  For now we'll do that.
            terminal('Restored project at: ' + pdir)
            return True

        else :
            terminal('Could not find project at: ' + pdir)
            return False


###############################################################################
########################## Component Level Functions ##########################
###############################################################################


    def initCompFiles (self, ctype, initInfo) :
        '''Get the files for this project according to the init specs. of the

        component.'''
        
        fls = initInfo['Files'].__iter__()
        for fs in fls :
            print fs
            fileName = ''; parentFolder = ''
            fGroup = initInfo['Files'][fs]
            for key, value in fGroup.iteritems() :
                if key == 'name' :
                    fileName = value
                elif key == 'location' :
                    if value :
                        parentFolder = value
                else :
                    pass

            if parentFolder :
                thisFile = os.path.join(self.projHome, parentFolder, fileName)
            else :
                thisFile = os.path.join(self.projHome, fileName)

            # Create source file name
            sourceFile = os.path.join(self.rpmHome, 'resources', 'lib_compTypes', ctype, 'lib_files', fileName)
            # Make the file if it is not already there
            if not os.path.isfile(thisFile) :
                if os.path.isfile(sourceFile) :
                    shutil.copy(sourceFile, thisFile)
                else :
                    open(thisFile, 'w').close()
                    if self.debugging == 'True' :
                        terminal('Created file: ' + thisFile)

    
    def initCompFolders (self, ctype, initInfo) :
        '''Get the folders for this project according to the init specs. of the
        component.'''

        fldrs = initInfo['Folders'].__iter__()
        for f in fldrs :
            folderName = ''; parentFolder = ''
            fGroup = initInfo['Folders'][f]
            for key, value in fGroup.iteritems() :
                if key == 'name' :

                    folderName = value
                elif key == 'location' :
                    if value != 'None' :
                        parentFolder = value
                else :
                    pass

            if parentFolder :
                thisFolder = os.path.join(self.projHome, parentFolder, folderName)
            else :
                thisFolder = os.path.join(self.projHome, folderName)

            # Create a source folder name in case there is one
            sourceFolder = os.path.join(self.rpmHome, 'resources', 'lib_compTypes', ctype, 'lib_folders', folderName)

            if not os.path.isdir(thisFolder) :
                if os.path.isdir(sourceFolder) :
                    shutil.copytree(sourceFolder, thisFolder)
                else :
                    os.mkdir(thisFolder)
                    if self.debugging == 'True' :
                        terminal('Created folder: ' + folderName)


    def initCompShared (self, initInfo) :
        '''Get the shared resources for this project according to the init
        specs. of the component.'''
        
        try :
            fldrs = initInfo['SharedResources'].__iter__()
            for f in fldrs :
                folderName = ''; parentFolder = ''
                fGroup = initInfo['SharedResources'][f]
                for key, value in fGroup.iteritems() :
                    if key == 'name' :
                        folderName = value
                    elif key == 'location' :
                        if value != 'None' :
                            parentFolder = value

                    elif key == 'shareLibPath' :
                        sharePath = value
                    else :
                        pass

                if parentFolder :
                    thisFolder = os.path.join(self.projHome, parentFolder, folderName)
                else :
                    thisFolder = os.path.join(self.projHome, folderName)

                # Create a source folder name
                sourceFolder = os.path.join(self.rpmHome, 'resources', 'lib_share', sharePath)
                # Create and copy the source stuff to the project
                if not os.path.isdir(thisFolder) :
                    if os.path.isdir(sourceFolder) :
                        shutil.copytree(sourceFolder, thisFolder)
        except :
            pass
        

    def initComponent (self, cid, ctype) :
        '''A function for initializing a component which is called by the
        component or project when a process is run.'''

        mod = 'project.initComponent()'

        # No need to init if it is done already
        if getattr(self, cid + 'Initialized') == False :
             # Pull the information from the project init xml file
            initInfo = getCompInitSettings(self.userHome, self.rpmHome, ctype)

            # Create all necessary (empty) folders
            self.initCompFolders(ctype, initInfo)
            # Bring in any known resources like macros, etc.
            self.initCompShared(initInfo)
            # Bring in any know files for this component
            self.initCompFiles(ctype, initInfo)

            setattr(self, cid + 'Initialized', True)

            return True   

######################################################################################################

    def initAuxiliaryComps (self, cid, ctype) :
        '''Initialize any auxiliary components associated with this component.'''

        print "Write me!"

######################################################################################################

    def addNewComponent (self, cid, ctype) :
        '''Add component to the current project by adding them to the component
        binding list and inserting component info into the project conf file.

        All supplied arguments need to be valid.  This function will fail if the
        type, source or ID are not valid or if the component already exsists in
        the binding order list.'''

        # Test for comp type section
        try :
            ct = self._projConfig['ComponentTypes']
        except :
            self._projConfig['ComponentTypes'] = {}

        # Test for this component and bail if it is there
        try :
            at = self._projConfig['Components'][cid]['compType']
            self.writeToLog('ERR', 'ID: [' + cid + '] cannot be added again.', 'project.addNewComponent()')
            return
        except :
            pass

        # First we add the type if it is not already in the project
        if ctype in self.validCompTypes :
            if not ctype in self._projConfig['ComponentTypes'] :
                self.addNewComponentType(ctype)

        if not cid in self._projConfig['ComponentTypes'][ctype]['validIdCodes'] :
            self.writeToLog('ERR', 'ID: [' + cid + '] not valid ID for [' + ctype + '] component type', 'project.addNewComponents()')
            return

        # Add to the installed components list for this type
        compList = []
        compList = self._projConfig['ComponentTypes'][ctype]['installedComponents']

        compList.append(cid)
        self._projConfig['ComponentTypes'][ctype]['installedComponents'] = compList

        # Read in the main settings file for this comp
        compSettings = getCompSettings(self.userHome, self.rpmHome, ctype)
        
        # The cid should be unique to the project so we add a section for it
        compItem = ConfigObj()
        compItem['Components'] = {}
        compItem['Components'][cid] = {}
        compItem['Components'][cid]['compType'] = ctype
        
#        compItem['Components'][cid].merge(compSettings[ctype + 'Setup'])
        
        self._projConfig.merge(compItem)
       
# Here we need to see if there are other things that need to go in this comp and get them.

        # Add component code to components list
        listOrder = []
        listOrder = self._projConfig['ProjectInfo']['componentList']
        listOrder.append(cid)
        self._projConfig['ProjectInfo']['componentList'] = listOrder

        # Add component code to binding order list
        if self._projConfig['ComponentTypes'][ctype]['inBindingList'] == 'True' :
            listOrder = []
            listOrder = self._projConfig['ProjectInfo']['projectComponentBindingOrder']
            listOrder.append(cid)
            self._projConfig['ProjectInfo']['projectComponentBindingOrder'] = listOrder

        self.writeOutProjConfFile = True
        self.writeToLog('MSG', 'Component added: ' + str(cid), 'project.addNewComponents()')


    def removeComponent (self, comp) :
        '''Remove a component from the current project by removing them from the

        component binding list and from their type information section.'''

        # Find out what kind of component type this is
        ctype = self._projConfig['Components'][comp]['compType']

        # Remove from components list first
        orderList = []
        orderList = self._projConfig['ProjectInfo']['componentList']
        if comp in orderList :
            orderList.remove(comp)
            self._projConfig['ProjectInfo']['componentList'] = orderList
            self.writeOutProjConfFile = True
        else :
            self.writeToLog('WRN', 'Component [' + comp + '] not found in component list', 'project.removeComponents()')

        # Remove from Binding order list
        orderList = []
        orderList = self._projConfig['ProjectInfo']['projectComponentBindingOrder']
        if comp in orderList :
            orderList.remove(comp)
            self._projConfig['ProjectInfo']['projectComponentBindingOrder'] = orderList
            self.writeOutProjConfFile = True
        else :
            self.writeToLog('WRN', 'Component [' + comp + '] not found in binding order list', 'project.removeComponents()')
        
        # Remove from the components installed list
        compList = self._projConfig['ComponentTypes'][ctype]['installedComponents']
        if comp in compList :
            compList.remove(comp)
            self._projConfig['ComponentTypes'][ctype]['installedComponents'] = compList
            self.writeOutProjConfFile = True
        
        # Remove the component's section from components
        if comp in self._projConfig['Components'] :
            del self._projConfig['Components'][comp]
            self.writeOutProjConfFile = True
            
        # Remove references in the ComponentTypes section if this is the last
        # component of its kind to be removed. 
        if len(self._projConfig['ComponentTypes'][ctype]['installedComponents']) == 0 :
            self.removeComponentType(ctype)

        # I guess if at least one of the above succeded we removed it
        if self.writeOutProjConfFile :
            self.writeToLog('MSG', 'Removed component: [' + comp + '] from project.', 'project.removeComponents()')


    def addNewComponentType (self, ctype) :
        '''This will add all the component type information to a project.'''

        # Test to see if the section is there, do not add if it is
        try:
            test = self._projConfig['ComponentTypes'][ctype]
            return False
        except :
            try :
                self._projConfig['ComponentTypes'][ctype] = {}
            except :
                self._projConfig['ComponentTypes'] = {}
                self._projConfig['ComponentTypes'][ctype] = {}

            self._projConfig.merge(getCompSettings(self.userHome, self.rpmHome, ctype))
            self.writeOutProjConfFile = True
            self.writeToLog('MSG', 'Component type: [' + ctype + '] added to project.', 'project.addNewComponentType()')
            return True
            

    def removeComponentType (self, ctype) :
        '''Remove a component type to the current project.  Before doing so, it
        must varify that the requested component type is valid.'''

        if len(self._projConfig['ComponentTypes'][ctype]['installedComponents']) == 0 :
            # Remove references in the ComponentType section
            del self._projConfig['ComponentTypes'][ctype]
            self.writeOutProjConfFile = True
            # FIXME: More should be done at this point to remove files, etc of the comp type.
            self.writeToLog('MSG', 'Component type: [' + ctype + '] removed from project.', 'project.removeComponentType()')
        else :
            self.writeToLog('WRN', 'Component type: [' + ctype + '] does not exsits.', 'project.removeComponentType()')


#    def importComponentSource (self, cid, source) :
#        '''Import the source for a component.  For some components, it is not
#        necessary to get data from outside the system.  For those that need it,
#        this function helps to that end.  This will test for the existence of
#        the source but will not do the actual import.  That will happen when the
#        component is initialized.'''
#        
#        # Check for the resouce and add it to the conf file if it exists.
#        if os.path.isfile(source) :
#            self._projConfig['Components'][cid]['source'] = source        
#            self.writeOutProjConfFile = True
#        else :
#            self.writeToLog('ERR', 'Path: [' + source + '] not valid.', 'project.addNewComponents()')
#            return


    def renderComponent (self, cid) :
        '''Render a single project component.  Before starting, make sure
        everything necessary has been initialized.'''

        ctype = self._projConfig['Components'][cid]['compType']

        # Check to see if this component is valid
        if not cid in self._projConfig['ProjectInfo']['componentList'] :
            self.writeToLog('ERR', 'Component: [' + cid + '] does not seem to be present in the project.', 'project.renderComponent()')
            return False
            
        # Initialize any auxiliary components that this component depends on
         if not self.initAuxiliaryComps(cid, ctype) :
            self.writeToLog('ERR', 'Component: [' + cid + '] failed to initialize.', 'project.renderComponent()')

            return False
           
        # Initialize this component.
        if not self.initComponent(cid, ctype) :
            self.writeToLog('ERR', 'Component: [' + cid + '] failed to initialize.', 'project.renderComponent()')

            return False
        
        # Check for dependencies for this component
        auxDepends = self._projConfig['ComponentTypes'][ctype]['auxDependencies']
        compDepends = self._projConfig['ComponentTypes'][ctype]['compDependencies']

        # First we will do a check on auxilary dependencies.  If any are
        # missing, this will fail and request that the aux be installed.
        if len(auxDepends) :
            # The dependencies should be listed in pairs 0 = auxilary, 1 = auxilary type
            for a in auxDepends :
                aux, atype = a.split(':')
                try :
                    a = self._projConfig['Auxiliaries'][aux]
                except :
                    self.writeToLog('ERR', 'Auxiliary component: [' + aux + '] not present, please install.', 'project.renderComponent()')
                    return False

        # Check for missing dependent components.  Require any missing to be
        # installed first before continuing.
        if len(compDepends) :
            # The dependencies should be listed in pairs 0 = component, 1 = component type
            for c in compDepends :
                comp, ctype = c.split(':')
                try :
                    c = self._projConfig['Components'][comp]
                except :
                    self.writeToLog('ERR', 'Component: [' + comp + '] not present, please install.', 'project.renderComponent()')
                    return False

        self.writeToLog('MSG', 'Rendered: [' + cid + ']', 'project.renderComponent()')
        
        return True


###############################################################################
########################## Auxiliary Level Functions ##########################
###############################################################################


    def getAuxiliary (self, aid = None, atype = None) :
        '''Create an auxiliary component object that is ready for processes to
        be run on it.'''

        if aid and aid not in self._projConfig['Auxiliaries'] :
            self.writeToLog('ERR', 'Auxiliary: [' + aid + '] not found.', 'project.getAuxiliary()')            
            return None
        
        if not aid in self._auxilaries :
            config = self._projConfig['Auxiliaries'][aid]
            atype = config['auxType']
            if not atype in auxiliary.auxiliaryTypes :
                self._auxilaries[aid] = auxiliary.auxiliary(self, config, None)
            else :
                self._auxilaries[aid] = auxiliary.auxiliaryTypes[atype](self, config, self._projConfig['AuxiliaryTypes'][atype])
        return self._auxilaries[aid]

        
    def addNewAuxiliary (self, aid, atype) :
        '''Add auxiliary component to the current project by inserting auxiliary
        component info into the project conf file.'''

        # Test for this auxiliary and bail if it is there
        try :
            at = self._projConfig['Auxiliaries'][aid]['auxType']
            self.writeToLog('ERR', 'ID: [' + aid + '] cannot be added again.', 'project.addNewAuxiliary()')
            return
        except :
            pass

        # Test for comp type section
        try :
            at = self._projConfig['AuxiliaryTypes']
        except :
            self._projConfig['AuxiliaryTypes'] = {}

        # First we add the aux type if it is not already in the project
        if atype in self.validAuxTypes :
            if not atype in self._projConfig['AuxiliaryTypes'] :
                self.addNewAuxiliaryType(atype)
        else :
            self.writeToLog('ERR', 'ID: [' + atype + '] not valid auxiliary to use in [' + self.projectType + '] project type', 'project.addNewAuxiliary()')            

        if not aid in self._projConfig['AuxiliaryTypes'][atype]['validIdCodes'] :
            self.writeToLog('ERR', 'ID: [' + aid + '] not valid ID for [' + atype + '] auxiliary component type', 'project.addNewAuxiliary()')
            return

        # Add to the installed auxiliary components list for this type
        auxList = []
        auxList = self._projConfig['AuxiliaryTypes'][atype]['installedAuxiliaries']
        auxList.append(aid)
        self._projConfig['AuxiliaryTypes'][atype]['installedAuxiliaries'] = auxList

        # Read in the main settings file for this aux comp
        auxSettings = getAuxSettings(self.userHome, self.rpmHome, atype)

        # The aid should be unique to the project so we add a section for it
        auxItem = ConfigObj()
        auxItem['Auxiliaries'] = {}
        auxItem['Auxiliaries'][aid] = {}
        auxItem['Auxiliaries'][aid]['auxType'] = atype
        self._projConfig.merge(auxItem)

        # Add component code to components list
        listOrder = []
        listOrder = self._projConfig['ProjectInfo']['auxiliaryList']
        listOrder.append(aid)
        self._projConfig['ProjectInfo']['auxiliaryList'] = listOrder


        self.writeOutProjConfFile = True
        self.writeToLog('MSG', 'Auxiliary added: ' + str(aid), 'project.addNewAuxiliary()')


    def removeAuxiliary (self, aux) :
        '''Remove an auxiliary component from the current project by removing
        its type information section.'''

        # Find out what kind of component type this is
        atype = self._projConfig['Auxiliaries'][aux]['auxType']

        # Remove from components list first
        orderList = []
        orderList = self._projConfig['ProjectInfo']['auxiliaryList']
        if aux in orderList :
            orderList.remove(aux)
            self._projConfig['ProjectInfo']['auxiliaryList'] = orderList
            self.writeOutProjConfFile = True
        else :
            self.writeToLog('WRN', 'Auxiliary [' + aux + '] not found in auxiliary list', 'project.removeAuxiliary()')

        # Remove from the components installed list
        auxList = self._projConfig['AuxiliaryTypes'][atype]['installedAuxiliaries']
        if aux in auxList :
            auxList.remove(aux)
            self._projConfig['AuxiliaryTypes'][atype]['installedAuxiliaries'] = auxList
            self.writeOutProjConfFile = True

        # Remove the component's section from auxiliaries
        if aux in self._projConfig['Auxiliaries'] :
            del self._projConfig['Auxiliaries'][aux]
            self.writeOutProjConfFile = True

        # Remove references in the ComponentTypes section if this is the last
        # component of its kind to be removed. 
        if len(self._projConfig['AuxiliaryTypes'][atype]['installedAuxiliaries']) == 0 :
            self.removeAuxiliaryType(atype)

        # I guess if at least one of the above succeded we removed it
        if self.writeOutProjConfFile :
            self.writeToLog('MSG', 'Removed component: [' + aux + '] from project.', 'project.removeAuxiliary()')


    def addNewAuxiliaryType (self, atype) :
        '''This will add all the auxiliary type information to a project.'''

        # Test to see if the section is there, do not add if it is
        try:
            test = self._projConfig['AuxiliaryTypes'][atype]
            return False
        except :
            try :
                self._projConfig['AuxiliaryTypes'][atype] = {}
            except :
                self._projConfig['AuxiliaryTypes'] = {}
                self._projConfig['AuxiliaryTypes'][atype] = {}

            self._projConfig.merge(getAuxSettings(self.userHome, self.rpmHome, atype))
            self.writeOutProjConfFile = True
            self.writeToLog('MSG', 'Auxiliary type: [' + atype + '] added to project.', 'project.addNewAuxiliaryType()')
            return True


    def removeAuxiliaryType (self, atype) :
        '''Remove an auxiliary type from the current project.  Before doing so, it
        must varify that the requested auxiliary type is valid.'''

        if len(self._projConfig['AuxiliaryTypes'][atype]['installedAuxiliaries']) == 0 :
            # Remove references in the AuxiliaryTypes section
            del self._projConfig['AuxiliaryTypes'][atype]
            self.writeOutProjConfFile = True
            # FIXME: More should be done at this point to remove files, etc of the aux type.
            self.writeToLog('MSG', 'Auxiliary type: [' + atype + '] removed from project.', 'project.removeAuxiliaryType()')
        else :
            self.writeToLog('WRN', 'Auxiliary type: [' + atype + '] does not exsits.', 'project.removeAuxiliaryType()')


###############################################################################
############################ System Level Functions ###########################
###############################################################################


    def changeSystemSetting (self, key, value) :
        '''Change global default setting (key, value) in the System section of
        the RPM user settings file.  This will write out changes
        immediately.'''

        if not self._userConfig['System'][key] == value :
            self._userConfig['System'][key] = value
            reportSysConfUpdate(self)
            terminal('Changed ' + key + ' to: ' + value)
            setattr(self, key, self._userConfig['System'][key] if self._userConfig else None)
        else :
            terminal(key + ' already set to ' + value)


###############################################################################
################################# Logging routines ############################
###############################################################################

# These have to do with keeping a running project log file.  Everything done is
# recorded in the log file and that file is trimmed to a length that is
# specified in the system settings.  Everything is channeled to the log file but
# depending on what has happened, they are classed in three levels:
#   1) Common event going to log and terminal
#   2) Warning event going to log and terminal if debugging is turned on
#   3) Error event going to the log and terminal

    def writeToLog (self, code, msg, mod = None) :
        '''Send an event to the log file. and the terminal if specified.
        Everything gets written to the log.  Whether a message gets written to
        the terminal or not depends on what type (code) it is.  There are four
        codes:
            MSG = General messages go to both the terminal and log file
            LOG = Messages that go only to the log file
            WRN = Warnings that go to the terminal and log file
            ERR = Errors that go to both the terminal and log file.'''

        # Build the mod line
        if mod :
            mod = mod + ': '
        else :
            mod = ''

        # Write out everything but LOG messages to the terminal
        if code != 'LOG' :
            terminal('\n' + code + ' - ' + msg)

        # Test to see if this is a live project by seeing if the project conf is
        # there.  If it is, we can write out log files.  Otherwise, why bother?
        if os.path.isfile(self.projConfFile) :

            # When are we doing this?
            ts = tStamp()
            
            # Build the event line
            if code == 'ERR' :
                eventLine = '\"' + ts + '\", \"' + code + '\", \"' + mod + msg + '\"'
            else :
                eventLine = '\"' + ts + '\", \"' + code + '\", \"' + msg + '\"'

            # Do we need a log file made?
            try :
                if not os.path.isfile(self.projLogFile) or os.path.getsize(self.projLogFile) == 0 :
                    writeObject = codecs.open(self.projLogFile, "w", encoding='utf_8')
                    writeObject.write('RPM event log file created: ' + ts + '\n')
                    writeObject.close()

                # Now log the event to the top of the log file using preAppend().
                self.preAppend(eventLine, self.projLogFile)

                # Write errors and warnings to the error log file
                if code == 'WRN' and self.debugging == 'True':
                    self.writeToErrorLog(eventLine)

                if code == 'ERR' :
                    self.writeToErrorLog(eventLine)

            except :
                terminal("Failed to write: " + msg)

        return


    def writeToErrorLog (self, eventLine) :
        '''In a perfect world there would be no errors, but alas there are and
        we need to put them in a special file that can be accessed after the
        process is run.  The error file from the previous session is deleted at
        the begining of each new run.'''

        try :
            # Because we want to read errors from top to bottom, we don't pre append
            # them to the error log file.
            if not os.path.isfile(self.projErrorLogFile) :
                writeObject = codecs.open(self.projErrorLogFile, "w", encoding='utf_8')
            else :
                writeObject = codecs.open(self.projErrorLogFile, "a", encoding='utf_8')

            # Write and close
            writeObject.write(eventLine + '\n')
            writeObject.close()
        except :
            terminal(eventLine)

        return


    def trimLog (self, projLogLineLimit = 1000) :
        '''Trim the system log file.  This will take an existing log file and
        trim it to the amount specified in the system file.'''

        # Of course this isn't needed if there isn't even a log file
        if os.path.isfile(self.projLogFile) :

            # Change this to an int()
            projLogLineLimit = int(projLogLineLimit)
            
            # Read in the existing log file
            readObject = codecs.open(self.projLogFile, "r", encoding='utf_8')
            lines = readObject.readlines()
            readObject.close()

            # Process only if we have enough lines
            if len(lines) > projLogLineLimit :
                
                writeObject = codecs.open(self.projLogFile, "w", encoding='utf_8')
                lineCount = 0
                for line in lines :
                    if projLogLineLimit > lineCount :
                        writeObject.write(line)
                        lineCount +=1

                writeObject.close()

        return


    def preAppend (self, line, file_name) :
        '''Got the following code out of a Python forum.  This will pre-append a
        line to the begining of a file.'''

        fobj = fileinput.FileInput(file_name, inplace=1)
        first_line = fobj.readline()
        sys.stdout.write("%s\n%s" % (line, first_line))
        for line in fobj:
            sys.stdout.write("%s" % line)

        fobj.close()


