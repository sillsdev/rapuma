#!/usr/bin/python
# -*- coding: utf_8 -*-

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

import codecs, os, zipfile, shutil
from configobj import ConfigObj

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.core.proj_config        import ProjConfig
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog


class ProjBackup (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.pid            = pid
        self.tools          = Tools()
        self.rapumaHome     = os.environ.get('RAPUMA_BASE')
        self.userHome       = os.environ.get('RAPUMA_USER')
        self.user           = UserConfig()
        self.userConfig     = self.user.userConfig
        self.projHome       = None
        self.local          = None
        self.projConfig     = None
        self.log            = None
        self.finishInit()

        # Log messages for this module
        self.errorCodes     = {

            '0000' : ['MSG', 'Placeholder message'],
            '0220' : ['LOG', 'Project [<<1>>] already registered in the system.'],
            '0240' : ['ERR', 'Could not find/open the Project configuration file for [<<1>>]. Project could not be registered!'],

            '0610' : ['ERR', 'The [<<1>>]. project is not registered. No backup was done.'],
            '0620' : ['ERR', 'User backup storage path not yet configured!'],
            '0630' : ['MSG', 'Backup for [<<1>>] created and saved to: [<<2>>]']

        }


    def finishInit (self, projHome = None) :
        '''Finishing collecting settings that would be needed for most
        functions in this module.'''

#        import pdb; pdb.set_trace()

        # Look for an existing project home path
        if self.userConfig['Projects'].has_key(self.pid) :
            localProjHome   = self.userConfig['Projects'][self.pid]['projectPath']
        else :
            localProjHome   = ''
        # Testing: The local project home wins over a user provided one
        if localProjHome :
            self.projHome   = localProjHome
        elif projHome :
            self.projHome   = projHome
        
        # If a projHome was succefully found, we can go on
        if self.projHome : 
            self.local      = ProjLocal(self.pid)
            self.projConfig = ProjConfig(self.local).projConfig
            self.log        = ProjLog(self.pid)


###############################################################################
############################## General Functions ##############################
###############################################################################
####################### Error Code Block Series = 0200 ########################
###############################################################################


    def registerProject (self, pid) :
        '''Do a basic project registration with information available in a
        project backup.'''

        # If this is a new project to the system, we should have a projHome
        # by now so we can try to get the projConfig now
        self.local          = ProjLocal(pid)
        self.projConfig     = ProjConfig(self.local).projConfig

        if len(self.projConfig) :
            pName           = self.projConfig['ProjectInfo']['projectName']
            pid             = self.projConfig['ProjectInfo']['projectIDCode']
            pmid            = self.projConfig['ProjectInfo']['projectMediaIDCode']
            pCreate         = self.projConfig['ProjectInfo']['projectCreateDate']
            if not self.userConfig['Projects'].has_key(pid) :
                self.tools.buildConfSection(self.userConfig['Projects'], pid)
                self.userConfig['Projects'][pid]['projectName']         = pName
                self.userConfig['Projects'][pid]['projectMediaIDCode']  = pmid
                self.userConfig['Projects'][pid]['projectPath']         = self.projHome
                self.userConfig['Projects'][pid]['projectCreateDate']   = pCreate
                self.tools.writeConfFile(self.userConfig)
            else :
                self.log.writeToLog(self.errorCodes['0220'], [pid])
        else :
            self.log.writeToLog(self.errorCodes['0240'], [pid])



###############################################################################
########################## Archive Project Functions ##########################
###############################################################################
####################### Error Code Block Series = 0400 ########################
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
            # These are specific files in the macro folder we don't want
            excludeFiles.append(os.path.join(root, 'macLink.tex'))
            excludeFiles.append(os.path.join(root, 'settings.tex'))
            # Now do a more general search
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

        # Exclude all PDFs from the Deliverables folder
        for root, dirs, files in os.walk(self.local.projDeliverablesFolder) :
            for fileName in files :
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
            path = self.tools.resolvePath(path)
            if os.path.isdir(path) :
                archTarget = os.path.join(path, archName)
            else :
                self.tools.terminal('\nError: The path given is not valid: [' + path + ']\n')
                self.tools.dieNow()
        elif os.path.isdir(userArchives) :
            archTarget = os.path.join(userArchives, archName)
        elif os.path.isdir(os.path.dirname(aProject.local.projHome)) :
            # Default to the dir just above the project
            archTarget = os.path.dirname(aProject.local.projHome)
        else :
            self.tools.terminal('\nError: Cannot resolve a path to create the archive file!\n')
            self.tools.dieNow()

        # Get a list of files we don't want
        excludeFiles = self.makeExcludeFileList()

        self.zipUpProject(archTarget, excludeFiles)

        # Rename the source dir to indicate it was archived
        bakArchProjDir = aProject.local.projHome + '(archived)'
        if os.path.isdir(bakArchProjDir) :
            self.tools.terminal('\nError: Cannot complete archival process!\n')
            self.tools.terminal('\nAnother archived version of this project exsits with the folder name of: ' + self.tools.fName(bakArchProjDir) + '\n')
            self.tools.terminal('\nPlease remove or rename it and then repete the process.\n')
            self.tools.dieNow()
        else :
            os.rename(aProject.local.projHome, bakArchProjDir)

        # Remove references from user rapuma.conf
        if uc.unregisterProject(pid) :
            self.tools.terminal('Removed [' + pid + '] from user configuration.\n')
        else :
            self.tools.terminal('Error: Failed to remove [' + pid + '] from user configuration.\n')

        # Finish here
        self.tools.terminal('Archive for [' + pid + '] created and saved to: ' + archTarget + '\n')


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
            self.tools.terminal('\nError: The path (or name) given is not valid: [' + archSource + ']\n')
            self.tools.dieNow()

        # Now set the target params
        if targetPath :
            if not os.path.isdir(targetPath) :
                self.tools.terminal('\nError: The path given is not valid: [' + targetPath + ']\n')
                self.tools.dieNow()
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
        self.tools.terminal('\nRapuma archive [' + pid + '] has been restored to: ' + archTarget + '\n')


###############################################################################
########################### Backup Project Functions ##########################
###############################################################################
####################### Error Code Block Series = 0600 ########################
###############################################################################


    def backupProject (self) :
        '''Backup a project. Send the compressed backup file to the user-specified
        backup folder. If none is specified, put the archive in cwd. If a valid
        path is specified, send it to that location. This is a very simplified
        backup so it will only keep one copy in any given location. If another
        copy exists, it will overwrite it.'''

        # First see if this is even a valid project
        if not self.userConfig['Projects'].has_key(self.pid) :
            self.log.writeToLog(self.errorCodes['0610'], [self.pid])

        # Set some paths and file names
        backupTarget = ''
        userBackups = ''
        backupName = self.pid + '.zip'
        if self.userConfig['Resources'].has_key('backups') :
            userBackups = self.tools.resolvePath(self.userConfig['Resources']['backups'])
        else :
            self.log.writeToLog(self.errorCodes['0620'])
        # Make sure the dir is there
        if not os.path.isdir(userBackups) :
            os.makedirs(userBackups)
        backupTarget = os.path.join(userBackups, backupName)

        # Zip up but use a list of files we don't want
        self.zipUpProject(backupTarget, self.makeExcludeFileList())

        # Finish here
        self.log.writeToLog(self.errorCodes['0630'], [self.pid,backupTarget])
        return True


    def restoreBackup (self, projHome = None) :
        '''Restore a project from the user specified storage area. If that
        is not set, it will fail. The project will be restored to the default
        project area as specified in the Rapuma config. Rapuma will register 
        the project there.'''

        if projHome :
            self.finishInit(projHome)

        # Assuming the above, this will be the archive file name
        # Check to see if the archive exsists
        backup = os.path.join(self.tools.resolvePath(self.userConfig['Resources']['backups']), self.pid + '.zip')
        if not os.path.exists(self.tools.resolvePath(self.userConfig['Resources']['backups'])) :
            self.tools.terminal('\nError: The path (or name) given is not valid: [' + backup + ']\n')
            self.tools.dieNow()

#        import pdb; pdb.set_trace()
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
        self.registerProject(self.pid)

        # Finish here (We will leave the backup-backup in place)
        self.tools.terminal('\nRapuma backup [' + self.pid + '] has been restored to: ' + self.projHome + '\n')


###############################################################################
######################### Template Project Functions ##########################
###############################################################################
####################### Error Code Block Series = 0800 ########################
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
        self.tools.terminal('\nCompleted creating template: ' + self.tools.fName(target) + '\n')


    def templateToProject (self, uc, projHome, pid, tid, pname, source = None) :
        '''Create a new project based on the provided template ID. This
        function is called from newProject() so all preliminary checks
        have been done. It should be good to go.'''

        # Test to see if the project is already there
        if os.path.isdir(projHome) :
            self.tools.terminal('\nError: Project [' + pid + '] already exsits.')
            self.tools.dieNow()

        if not source :
            source = os.path.join(uc.userConfig['Resources']['templates'], tid + '.zip')

        # Validate template
        if not os.path.isfile(source) :
            self.tools.terminal('\nError: Template not found: ' + source)
            self.tools.dieNow()

        # Unzip the template in place to start the new project
        with zipfile.ZipFile(source, 'r') as myzip :
            myzip.extractall(projHome)

        # Peek into the project
        pc = ConfigObj(os.path.join(projHome, 'Config', 'project.conf'), encoding='utf-8')

        pc['ProjectInfo']['projectName']               = pname
        pc['ProjectInfo']['projectCreateDate']         = self.tools.tStamp()
        pc['ProjectInfo']['projectIDCode']             = pid
        pc.filename                                    = os.path.join(projHome, 'Config', 'project.conf')
        pc.write()

        # Get the media type from the newly placed project for registration
        projectMediaIDCode = pc['ProjectInfo']['projectMediaIDCode']

        # Register the new project
        uc.registerProject(pid, pname, projectMediaIDCode, projHome)
        
        # Report what happened
        self.tools.terminal('A new project [' + pid + '] has been created based on the [' + tid + '] template.')


###############################################################################
############################ Cloud Backup Functions ###########################
###############################################################################
####################### Error Code Block Series = 1000 ########################
###############################################################################


    def pullFromCloud (self, projHome = None) :
        '''Pull data from cloud storage and merge/replace local data.
        Do a full backup first before starting the actual pull operation.'''

        # In case there was not enough info at init time
        if projHome :
            self.finishInit(projHome)

        # Do not do anything until we have done a backup
        self.backupProject()

        # Get the paths we need
        cloud               = os.path.join(self.tools.resolvePath(self.userConfig['Resources']['cloud']), self.pid)

        # Get a total list of files from the project
        cn = 0
        cr = 0
        for folder, subs, files in os.walk(cloud):
            for fileName in files:
                if not os.path.isdir(folder.replace(cloud, self.projHome)) :
                    os.makedirs(folder.replace(cloud, self.projHome))
                cFile = os.path.join(folder, fileName)
                pFile = os.path.join(folder, fileName).replace(cloud, self.projHome)
                if not os.path.isfile(pFile) :
                    shutil.copy(cFile, pFile)
                    cn +=1
                elif self.tools.isOlder(pFile, cFile) :
                    if os.path.isfile(pFile) :
                        os.remove(pFile)
                    shutil.copy(cFile, pFile)
                    cr +=1
        # Report what happened
        self.tools.terminal('\nCompleted pulling data from the cloud.\n')
        if cn == 0 and cr == 0 :
            self.tools.terminal('\tNo files updated.\n')
        else :
            if cn > 0 :
                self.tools.terminal('\tAdded: ' + str(cn) + ' file(s).\n')
            if cr > 0 :
                self.tools.terminal('\tUpdated: ' + str(cr) + ' file(s).\n')

        # If this is a new project we will need to register it now
        self.registerProject(self.pid)


    def pushToCloud (self) :
        '''Push local project data to the cloud. If a file in the cloud is
        older than the project file, it will be sent. Otherwise, it will
        be skipped.'''

        cloud = os.path.join(self.tools.resolvePath(self.userConfig['Resources']['cloud']), self.pid)

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
                    elif self.tools.isOlder(cFile, pFile) :
                        if os.path.isfile(cFile) :
                            os.remove(cFile)
                        shutil.copy(pFile, cFile)
                        cr +=1
        # Report what happened
        self.tools.terminal('\nCompleted pushing/saving data to the cloud.\n')
        if cn == 0 and cr == 0 :
            self.tools.terminal('\tNo files updated.\n')
        else :
            if cn > 0 :
                self.tools.terminal('\tAdded: ' + str(cn) + ' file(s).\n')
            if cr > 0 :
                self.tools.terminal('\tUpdated: ' + str(cr) + ' file(s).\n')



