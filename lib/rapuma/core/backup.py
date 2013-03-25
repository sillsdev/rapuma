#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project backup/archive operations.

###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from configobj import ConfigObj

# Load the local classes
from rapuma.core.tools          import *
from rapuma.core.proj_config    import ProjConfig
from rapuma.core.user_config    import UserConfig
from rapuma.core.proj_local     import ProjLocal
from rapuma.core.proj_log       import ProjLog


class ProjBackup (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.rapumaHome     = os.environ.get('RAPUMA_BASE')
        self.userHome       = os.environ.get('RAPUMA_USER')
        self.user           = UserConfig(self.rapumaHome, self.userHome)
        self.userConfig     = self.user.userConfig
        self.pid            = pid
        self.projHome       = None
        self.local          = None
        self.projConfig     = None
        self.finishInit()


    def finishInit (self, projHome = None) :
        '''Finishing collecting settings that would be needed for most
        functions in this module.'''

        # Look for an existing project home path
        try :
            localProjHome   = self.userConfig['Projects'][self.pid]['projectPath']
        except :
            localProjHome   = ''
        # Testing: The local project home wins over a user provided one
        if localProjHome and not projHome :
            self.projHome   = localProjHome
        elif projHome :
            self.projHome   = projHome
        
        # If a projHome was succefully found, we can go on
        if self.projHome : 
            self.local      = ProjLocal(self.rapumaHome, self.userHome, self.projHome)
            self.projConfig = ProjConfig(self.local).projConfig


    def registerProject (self) :
        '''Do a basic project registration with information available in a
        project backup.'''

        # If this is a new project to the system, we should have a projHome
        # by now so we can try to get the projConfig now
        self.local      = ProjLocal(self.rapumaHome, self.userHome, self.projHome)
        self.projConfig = ProjConfig(self.local).projConfig

        if len(self.projConfig) :
            pName = self.projConfig['ProjectInfo']['projectName']
            pid = self.projConfig['ProjectInfo']['projectIDCode']
            pmid = self.projConfig['ProjectInfo']['projectMediaIDCode']
            pCreate = self.projConfig['ProjectInfo']['projectCreateDate']
            if not isConfSection(self.userConfig['Projects'], pid) :
                buildConfSection(self.userConfig['Projects'], pid)
                self.userConfig['Projects'][pid]['projectName']         = pName
                self.userConfig['Projects'][pid]['projectMediaIDCode']  = pmid
                self.userConfig['Projects'][pid]['projectPath']         = self.projHome
                self.userConfig['Projects'][pid]['projectCreateDate']   = pCreate
                writeConfFile(self.userConfig)
            else :
                dieNow('Project already registered in the system.\n\n')
        else :
            dieNow('Error: Could not find/open the Project configuration file. Project could not be registered!\n\n')



###############################################################################
########################## Archive Project Functions ##########################
###############################################################################

    def makeExcludeFileList (self) :
        '''Return a list of files that are not necessary to be included in a backup
        template or an archive. These will be all auto-generated files that containe system-
        specific paths, etc.'''

        excludeFiles        = []
        excludeTypes        = ['delayed', 'log', 'notepages', 'parlocs', 'pdf', 'tex', 'piclist', 'adj']

        # Process the components folder
        for root, dirs, files in os.walk(self.local.projComponentsFolder) :
            for fileName in files :
                # Get rid of backup files
                if fileName[-1] == '~' :
                    excludeFiles.append(os.path.join(root, fileName))
                    continue
                ext = os.path.splitext(fileName)[1][1:]
                if ext in excludeTypes :
                    # A special indicator for file we want to keep
                    if fileName.find('-ext.') > 0 :
                        continue
                    excludeFiles.append(os.path.join(root, fileName))

        # Special processing of the Macros folder (in this case we
        # want to keep most of the .tex files.)
        for root, dirs, files in os.walk(self.local.projMacrosFolder) :
            for fileName in files :
                # Get rid of backup files
                if fileName[-1] == '~' :
                    excludeFiles.append(os.path.join(root, fileName))
                    continue
                ext = os.path.splitext(fileName)[1][1:]
                if ext in excludeTypes :
                    # A special indicator for file we want to keep
                    if fileName.find('-ext.') > 0 :
                        continue
                    elif fileName.find('macLink.tex') > 0 :
                        excludeFiles.append(os.path.join(root, fileName))
                    elif fileName.find('_set.tex') > 0 :
                        excludeFiles.append(os.path.join(root, fileName))

        return excludeFiles


    def archiveProject (self, pid, path = None) :
        '''Archive a project. Send the compressed archive file to the user-specified
        archive folder. If none is specified, put the archive in cwd. If a valid
        path is specified, send it to that location. Like backup, this too will
        overwrite any existing file of the same name. The difference is that this
        will also disable the project so it cannot be accesses by Rapuma. When a
        project is archived, all work should cease on the project.'''

        # Make a private project object just for archiving
        aProject = initProject(pid)
        # Set some paths and file names
        archName = aProject.projectIDCode + '.rapuma'
        userArchives = uc.userConfig['Resources']['archives']
        archTarget = ''
        if path :
            path = resolvePath(path)
            if os.path.isdir(path) :
                archTarget = os.path.join(path, archName)
            else :
                terminal('\nError: The path given is not valid: [' + path + ']\n')
                dieNow()
        elif os.path.isdir(userArchives) :
            archTarget = os.path.join(userArchives, archName)
        elif os.path.isdir(os.path.dirname(aProject.local.projHome)) :
            # Default to the dir just above the project
            archTarget = os.path.dirname(aProject.local.projHome)
        else :
            terminal('\nError: Cannot resolve a path to create the archive file!\n')
            dieNow()

        # Get a list of files we don't want
        excludeFiles = self.makeExcludeFileList()

        self.zipUpProject(archTarget, excludeFiles)

        # Rename the source dir to indicate it was archived
        bakArchProjDir = aProject.local.projHome + '(archived)'
        if os.path.isdir(bakArchProjDir) :
            terminal('\nError: Cannot complete archival process!\n')
            terminal('\nAnother archived version of this project exsits with the folder name of: ' + fName(bakArchProjDir) + '\n')
            terminal('\nPlease remove or rename it and then repete the process.\n')
            dieNow()
        else :
            os.rename(aProject.local.projHome, bakArchProjDir)

        # Remove references from user rapuma.conf
        if uc.unregisterProject(pid) :
            terminal('Removed [' + pid + '] from user configuration.\n')
        else :
            terminal('Error: Failed to remove [' + pid + '] from user configuration.\n')

        # Finish here
        terminal('Archive for [' + pid + '] created and saved to: ' + archTarget + '\n')


    def zipUpProject (self, target, excludeFiles = None) :
        '''Zip up a project and deposit it to target location. Be sure to strip
        out all all auto-created, user-specific files that could mess up a
        transfer to another system. This goes for archives and backups'''

        # In case an exclude list is not given
        if not excludeFiles :
            excludeFiles = []

        # Do the zip magic here
        root_len = len(self.projHome)
        with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as myzip :
            for root, dirs, files in os.walk(self.projHome) :
                # Chop off the part of the path we do not need to store
                zip_root = os.path.abspath(root)[root_len:]
                for f in files :
                    if os.path.join(root, f) in excludeFiles :
                        continue
                    if not f[-1] == '~' :
                        fn, fx = os.path.splitext(f)
                        fullpath = os.path.join(root, f)
                        zip_name = os.path.join(zip_root, f)
                        myzip.write(fullpath, zip_name, zipfile.ZIP_DEFLATED)


    def restoreArchive (self, pid, targetPath, sourcePath = None) :
        '''Restore a project from the user specified storage area or sourcePath if 
        specified. Use targetPath to specify where the project will be restored.
        Rapuma will register the project there.'''

        # Check to see if the user included the extention
        try :
            pid.split('.')[1] == 'rapuma'
            archName = pid
            pid = pid.split('.')[0]
        except :
            archName = pid + '.rapuma'

        archSource = ''
        archTarget = ''
        userArchives = ''

        # First look for the archive that is to be restored
        if sourcePath :
            if os.path.isdir(sourcePath) :
                archSource = os.path.join(sourcePath, archName)
        elif os.path.isdir(uc.userConfig['Resources']['archives']) :
            userArchives = uc.userConfig['Resources']['archives']
            archSource = os.path.join(userArchives, archName)
        else :
            terminal('\nError: The path (or name) given is not valid: [' + archSource + ']\n')
            dieNow()

        # Now set the target params
        if targetPath :
            if not os.path.isdir(targetPath) :
                terminal('\nError: The path given is not valid: [' + targetPath + ']\n')
                dieNow()
            else :
                archTarget = os.path.join(targetPath, pid)

        # If we made it this far, extract the archive
        with zipfile.ZipFile(archSource, 'r') as myzip :
            myzip.extractall(archTarget)

        # Permission for executables is lost in the zip, fix it here
        for folder in ['Scripts', os.path.join('Macros', 'User')] :
            fixExecutables(os.path.join(archTarget, folder))

        # Add project to local Rapuma project registry
        # To do this we need to open up the restored project config file
        # and pull out some settings.
        local       = ProjLocal(rapumaHome, userHome, archTarget)
        pc          = ProjConfig(local)
        log         = ProjLog(local, uc)
        aProject    = Project(uc.userConfig, pc.projConfig, local, log, systemVersion)
    #    import pdb; pdb.set_trace()
        uc.registerProject(aProject.projectIDCode, aProject.projectName, aProject.projectMediaIDCode, aProject.local.projHome)

        # Finish here
        terminal('\nRapuma archive [' + pid + '] has been restored to: ' + archTarget + '\n')


###############################################################################
########################### Backup Project Functions ##########################
###############################################################################

    def backupProject (self) :
        '''Backup a project. Send the compressed backup file to the user-specified
        backup folder. If none is specified, put the archive in cwd. If a valid
        path is specified, send it to that location. This is a very simplified
        backup so it will only keep one copy in any given location. If another
        copy exists, it will overwrite it.'''

        # Set some paths and file names
        backupName = self.pid + '.zip'
        userBackups = resolvePath(self.userConfig['Resources']['backups'])
        backupTarget = ''
        if os.path.isdir(userBackups) :
            backupTarget = os.path.join(userBackups, backupName)
        else :
            terminal('\nError: User backup storage path not yet configured!\n')
            dieNow()

        # Zip up but use a list of files we don't want
        self.zipUpProject(backupTarget, self.makeExcludeFileList())

        # Finish here
        terminal('Backup for [' + self.pid + '] created and saved to: ' + backupTarget + '\n')


    def restoreBackup (self, projHome = None) :
        '''Restore a project from the user specified storage area. If that
        is not set, it will fail. The project will be restored to the default
        project area as specified in the Rapuma config. Rapuma will register 
        the project there.'''

        if projHome :
            self.finishInit(projHome)

        # Assuming the above, this will be the archive file name
        # Check to see if the archive exsists
        backup = os.path.join(resolvePath(self.userConfig['Resources']['backups']), self.pid + '.zip')
        if not os.path.exists(resolvePath(self.userConfig['Resources']['backups'])) :
            terminal('\nError: The path (or name) given is not valid: [' + backup + ']\n')
            dieNow()


        # If there is an exsiting project make a temp backup in 
        # case something goes dreadfully wrong
        if os.path.isdir(self.projHome) :
            # Remove old backup-backup
            if os.path.exists(self.projHome + '.bak') :
                shutil.rmtree(self.projHome + '.bak')
            # Make a fresh copy of the backup-backup
            shutil.copytree(self.projHome, self.projHome + '.bak')
            # For succeful extraction we need to delete the target
            if os.path.exists(self.projHome) :
                shutil.rmtree(self.projHome)

#        import pdb; pdb.set_trace()

        # If we made it this far, extract the archive
        with zipfile.ZipFile(backup, 'r') as myzip :
            myzip.extractall(self.projHome)

        # Permission for executables is lost in the zip, fix them here
        fixExecutables(self.projHome)

        # If this is a new project we will need to register it now
        self.registerProject()

        # Finish here (We will leave the backup-backup in place)
        terminal('\nRapuma backup [' + self.pid + '] has been restored to: ' + self.projHome + '\n')


###############################################################################
######################### Template Project Functions ##########################
###############################################################################

    def projectToTemplate (self, pid, tid) :
        '''Preserve critical project information in a template. The pid is the project
        that the template will be bassed from. The tid will be provided by the user for
        this operation and used to create new projects.'''

        # Set source and target
        projHome            = uc.userConfig['Projects'][pid]['projectPath']
        templateDir         = uc.userConfig['Resources']['templates']
        targetDir           = os.path.join(templateDir, tid)
        target              = os.path.join(templateDir, tid + '.zip')
        source              = projHome

        # Make a temp copy of the project that we can manipulate
        shutil.copytree(source, targetDir)

        # Now make the config files generic for use with any project
        pc = ConfigObj(os.path.join(targetDir, 'Config', 'project.conf'), encoding='utf-8')
        aProject = initProject(pc['ProjectInfo']['projectIDCode'])
        pc['ProjectInfo']['projectName']                = ''
        pc['ProjectInfo']['projectIDCode']              = ''
        pc['ProjectInfo']['projectCreateDate']          = ''
        pc['ProjectInfo']['projectCreateDate']          = ''
        for c in pc['Components'].keys() :
            compDir = os.path.join(targetDir, 'Components', c)
            if os.path.isdir(compDir) :
                shutil.rmtree(compDir)
            del pc['Components'][c]
        pc.filename                                     = os.path.join(targetDir, 'Config', 'project.conf')
        pc.write()
        # Kill the log file
        os.remove(os.path.join(targetDir, 'rapuma.log'))

        # Exclude files
        excludeFiles = makeExcludeFileList()

        # Zip it up using the above params
        root_len = len(targetDir)
        with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as myzip :
            for root, dirs, files in os.walk(targetDir):
                # Chop off the part of the path we do not need to store
                zip_root = os.path.abspath(root)[root_len:]
                for f in files:
                    if f[-1] == '~' :
                        continue
                    elif f in excludeFiles :
                        continue
                    elif f.rfind('.') != -1 :
                        fullpath = os.path.join(root, f)
                        zip_name = os.path.join(zip_root, f)
                        myzip.write(fullpath, zip_name, zipfile.ZIP_DEFLATED)

        # Remove the temp project dir we made
        shutil.rmtree(targetDir)
        terminal('\nCompleted creating template: ' + fName(target) + '\n')


    def templateToProject (self, uc, projHome, pid, tid, pname, source = None) :
        '''Create a new project based on the provided template ID. This
        function is called from newProject() so all preliminary checks
        have been done. It should be good to go.'''

        # Test to see if the project is already there
        if os.path.isdir(projHome) :
            terminal('\nError: Project [' + pid + '] already exsits.')
            dieNow()

        if not source :
            source = os.path.join(uc.userConfig['Resources']['templates'], tid + '.zip')

        # Validate template
        if not os.path.isfile(source) :
            terminal('\nError: Template not found: ' + source)
            dieNow()

        # Unzip the template in place to start the new project
        with zipfile.ZipFile(source, 'r') as myzip :
            myzip.extractall(projHome)

        # Peek into the project
        pc = ConfigObj(os.path.join(projHome, 'Config', 'project.conf'), encoding='utf-8')

        pc['ProjectInfo']['projectName']               = pname
        pc['ProjectInfo']['projectCreateDate']         = tStamp()
        pc['ProjectInfo']['projectIDCode']             = pid
        pc.filename                                    = os.path.join(projHome, 'Config', 'project.conf')
        pc.write()

        # Get the media type from the newly placed project for registration
        projectMediaIDCode = pc['ProjectInfo']['projectMediaIDCode']

        # Register the new project
        uc.registerProject(pid, pname, projectMediaIDCode, projHome)
        
        # Report what happened
        terminal('A new project [' + pid + '] has been created based on the [' + tid + '] template.')


###############################################################################
############################ Cloud Backup Functions ###########################
###############################################################################

    def pullFromCloud (self, pid) :
        '''Pull data from cloud storage and merge/replace local data.
        Do a full backup first before starting the actual pull operation.'''


    # FIXME: Need to add project addition to this for projects that are not
    # registered with the local system.


        # Do not do anything until we have done a backup
        backupProject(pid)

        # Get the paths we need
        cloud               = os.path.join(uc.userConfig['Resources']['cloud'], pid)
        projHome            = uc.userConfig['Projects'][pid]['projectPath']

        # Get a total list of files from the project
        cn = 0
        cr = 0
        for folder, subs, files in os.walk(cloud):
            for fileName in files:
                if not os.path.isdir(folder.replace(cloud, projHome)) :
                    os.makedirs(folder.replace(cloud, projHome))
                cFile = os.path.join(folder, fileName)
                pFile = os.path.join(folder, fileName).replace(cloud, projHome)
                if not os.path.isfile(pFile) :
                    shutil.copy(cFile, pFile)
                    cn +=1
                elif isOlder(cFile, pFile) :
                    if os.path.isfile(pFile) :
                        os.remove(pFile)
                    shutil.copy(cFile, pFile)
                    cr +=1
        # Report what happened
        terminal('\nCompleted pulling data from the cloud.\n')
        if cn == 0 and cr == 0 :
            terminal('\tNo files updated.\n')
        else :
            if cn > 0 :
                terminal('\tAdded: ' + str(cn) + ' file(s).\n')
            if cr > 0 :
                terminal('\tUpdated: ' + str(cr) + ' file(s).\n')


    def pushToCloud (self) :
        '''Push local project data to the cloud. If a file in the cloud is
        older than the project file, it will be sent. Otherwise, it will
        be skipped.'''

        cloud = os.path.join(resolvePath(self.userConfig['Resources']['cloud']), self.pid)

        # Make a cloud
        if not os.path.isdir(cloud) :
            os.makedirs(cloud)

        # Get a list of files we do not want
        excludeFiles        = self.makeExcludeFileList()

        # Get a total list of files from the project
        cn = 0
        cr = 0
        for folder, subs, files in os.walk(self.projHome):
            for fileName in files:
                # Do not include any backup files we find
                if fileName[-1] == '~' :
                    continue
                if os.path.join(folder, fileName) not in excludeFiles :
                    if not os.path.isdir(folder.replace(self.projHome, cloud)) :
                        os.makedirs(folder.replace(self.projHome, cloud))
                    cFile = os.path.join(folder, fileName).replace(self.projHome, cloud)
                    pFile = os.path.join(folder, fileName)
                    if not os.path.isfile(cFile) :
                        shutil.copy(pFile, cFile)
                        cn +=1
                    # Otherwise if the cloud file is older than
                    # the project file, refresh it
                    elif isOlder(cFile, pFile) :
                        if os.path.isfile(cFile) :
                            os.remove(cFile)
                        shutil.copy(pFile, cFile)
                        cr +=1
        # Report what happened
        terminal('\nCompleted pushing/saving data to the cloud.\n')
        if cn == 0 and cr == 0 :
            terminal('\tNo files updated.\n')
        else :
            if cn > 0 :
                terminal('\tAdded: ' + str(cn) + ' file(s).\n')
            if cr > 0 :
                terminal('\tUpdated: ' + str(cr) + ' file(s).\n')



