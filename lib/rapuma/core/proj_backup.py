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
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog
from rapuma.project.proj_config     import ProjConfig


class ProjBackup (object) :

    def __init__(self, pid, gid = None) :
        '''Intitate the whole class and create the object.'''

        self.pid            = pid
        self.tools          = Tools()
        self.rapumaHome     = os.environ.get('RAPUMA_BASE')
        self.userHome       = os.environ.get('RAPUMA_USER')
        self.user           = UserConfig()
        self.userConfig     = self.user.userConfig
        self.projHome       = None
        self.local          = None
        self.log            = None

        # Log messages for this module
        self.errorCodes     = {

            '0000' : ['MSG', 'Placeholder message'],
            '0220' : ['LOG', 'Project [<<1>>] already registered in the system.'],
            '0240' : ['ERR', 'Could not find/open the Project configuration file for [<<1>>]. Project could not be registered!'],

            '0610' : ['ERR', 'The [<<1>>]. project is not registered. No backup was done.'],
            '0620' : ['ERR', 'User backup storage path not yet configured!'],
            '0630' : ['MSG', 'Backup for [<<1>>] created and saved to: [<<2>>]'],

            '4110' : ['MSG', 'Completed pushing/saving data to the cloud.'],
            '4120' : ['MSG', 'No files updated.'],
            '4130' : ['MSG', 'Added: <<1>> file(s).'],
            '4140' : ['MSG', 'Updated: <<1>> file(s)'],
            '4150' : ['ERR', 'The cloud project [<<1>>] you want to push to is owned by [<<2>>]. Use force (-f) to change the owner to your user ID.'],
            '4160' : ['ERR', 'The cloud project [<<1>>] is newer than the local copy. If you seriously want to overwrite it, use force (-f) to do so.'],

            '4210' : ['MSG', 'Completed pulling/restoring data from the cloud.'],
            '4220' : ['ERR', 'Cannot resolve provided path: [<<1>>]'],
            '4250' : ['ERR', 'The cloud project [<<1>>] you want to pull from is owned by [<<2>>]. Use force (-f) to pull the project and change the local owner ID.'],
            '4260' : ['ERR', 'The local project [<<1>>] is newer than the cloud copy. If you seriously want to overwrite it, use force (-f) to do so.'],
            '4270' : ['MSG', 'Restored the project [<<1>>] from the cloud copy. Local copy is owned by [<<2>>].']

        }

        # Finishing collecting settings that would be needed for most
        # functions in this module.

#        import pdb; pdb.set_trace()

        # Look for an existing project home path
        if self.userConfig['Projects'].has_key(self.pid) :
            localProjHome   = self.userConfig['Projects'][self.pid]['projectPath']
        else :
            localProjHome   = ''

        # Testing: The local project home wins over a user provided one
        if localProjHome :
            self.projHome   = localProjHome
        elif self.projHome :
            self.projHome   = projHome

        # If a projHome was succefully found, we can go on
        if self.projHome : 
            self.local      = ProjLocal(self.pid)
            self.log        = ProjLog(self.pid)


###############################################################################
############################## General Functions ##############################
###############################################################################
####################### Error Code Block Series = 0200 ########################
###############################################################################


    def registerProject (self, projHome) :
        '''Do a basic project registration with information available in a
        project config file found in projHome.'''

        pid                 = os.path.basename(projHome)
        projConfig          = self.getConfig(projHome)

        if len(projConfig) :
            pName           = projConfig['ProjectInfo']['projectName']
            pid             = projConfig['ProjectInfo']['projectIDCode']
            pmid            = projConfig['ProjectInfo']['projectMediaIDCode']
            pCreate         = projConfig['ProjectInfo']['projectCreateDate']
            if not self.userConfig['Projects'].has_key(pid) :
                self.tools.buildConfSection(self.userConfig['Projects'], pid)
                self.userConfig['Projects'][pid]['projectName']         = pName
                self.userConfig['Projects'][pid]['projectMediaIDCode']  = pmid
                self.userConfig['Projects'][pid]['projectPath']         = projHome
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
        excludeTypes        = ['delayed', 'log', 'notepages', 'parlocs', 'pdf', 'tex', 'piclist', 'adj', 'zip']

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

# FIXME: This will need some work 

        # Add project to local Rapuma project registry
        # To do this we need to open up the restored project config file
        # and pull out some settings.
        local       = ProjLocal(rapumaHome, userHome, archTarget)
        pc          = ProjConfig(pid)
        log         = ProjLog(pid)
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












# FIXME: Working here




    def cullBackups (self) :
        '''Remove any excess backups from the backup folder in
        this project.'''

        files = os.listdir(self.local.projBackupFolder)
        maxStoreBackups = ProjConfig(self.pid).projConfig['Backup']['maxStoreBackups']
        
        print maxStoreBackups, files


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
        projBackupFolder    = self.local.projBackupFolder
        backupName          = self.tools.fullFileTimeStamp() + '.zip'
        backupTarget        = os.path.join(projBackupFolder, backupName)

        # Make sure the dir is there
        if not os.path.isdir(projBackupFolder) :
            os.makedirs(projBackupFolder)

        # Cull out any excess backups
        self.cullBackups()

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
####################### Error Code Block Series = 4000 ########################
###############################################################################


    def isNewerThanCloud (self, cloud, projConfig) :
        '''Compare time stamps between the cloud and the local project.
        Return True if the local project is newer or the same age as
        the copy in the cloud. Return True if the project does not
        exist in the local copy of the cloud.'''

        # First see if it exists
        cConfig = self.getConfig(cloud)
        if not cConfig :
            return True
        # Compare if we made it this far
        cStamp = cConfig['Backup']['lastCloudPush']
        lStamp = projConfig['Backup']['lastCloudPush']
        if lStamp >= cStamp :
            return True


    def isNewerThanLocal (self, cloud, projConfig) :
        '''Compare time stamps between the cloud and the local project.
        Return True if the cloud project is newer or the same age as
        the local copy. Return True if the project does not exist in
        as a local copy.'''

        # First see if the local exists
        if not projConfig :
            return True

        # Compare if we made it this far
        cStamp = self.getConfig(cloud)['Backup']['lastCloudPush']
        pStamp = projConfig['Backup']['lastCloudPush']
        if cStamp >= pStamp :
            return True


    def getConfig (self, cloud) :
        '''Return a valid config object from cloud project.'''

        projCloudConfig = os.path.join(cloud, 'Config', 'project.conf')
        if os.path.exists(projCloudConfig) :
            return ConfigObj(projCloudConfig, encoding='utf-8')


    def getCloudOwner (self, cloud) :
        '''Return the owner of a specified cloud project.'''

        return self.getConfig(cloud)['Backup']['ownerID']


    def getLocalOwner (self) :
        '''Return the owner of a specified cloud project.'''

        return self.userConfig['System']['userID']


    def sameOwner (self, cloud) :
        '''Return True if the owner of a given cloud is the same as
        the system user. Also return True if the cloud owner is not
        present.'''

        # First check for existence
        if not self.getCloudOwner(cloud) :
            return True
        # Compare if we made it to this point
        if self.getCloudOwner(cloud) == self.getLocalOwner() :
            return True


    def setCloudPushTime (self, projConfig) :
        '''Set/reset the lastPush time stamp setting.'''

        projConfig['Backup']['lastCloudPush'] = self.tools.fullFileTimeStamp()
        self.tools.writeConfFile(projConfig)


    def buyCloud (self, projConfig) :
        '''Change the ownership on a project in the cloud by assigning
        your userID to the local project cloudOwnerID. Then, using force
        the next time the project is pushed to the cloud, you will own it.'''

        projOwnerID = self.userConfig['System']['userID']
        projConfig['Backup']['ownerID'] = projOwnerID
        self.tools.writeConfFile(projConfig)


    def buyLocal (self, projConfig) :
        '''Change the ownership on a local project by assigning your
        userID to it.'''

        projOwnerID = self.userConfig['System']['userID']
        projConfig['Backup']['ownerID'] = projOwnerID
        self.tools.writeConfFile(projConfig)


    def pushToCloud (self, force = False) :
        '''Push local project data to the cloud. If a file in the cloud is
        older than the project file, it will be sent. Otherwise, it will
        be skipped.'''

        # Make a cloud reference
        cloud = os.path.join(self.tools.resolvePath(self.userConfig['Resources']['cloud']), self.pid)
        if not os.path.isdir(cloud) :
            os.makedirs(cloud)

        def doPush (cloud) :
            '''When everything is sorted out do the push.'''

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
            self.log.writeToLog(self.errorCodes['4110'])
            if cn == 0 and cr == 0 :
                self.log.writeToLog(self.errorCodes['4120'])
            else :
                if cn > 0 :
                    self.log.writeToLog(self.errorCodes['4130'], [str(cn)])
                if cr > 0 :
                    self.log.writeToLog(self.errorCodes['4140'], [str(cr)])

        # Check for existence of this project in the cloud and who owns it
        projConfig = ProjConfig(self.pid).projConfig
        if not self.sameOwner(cloud) :
            if force :
                self.setCloudPushTime(projConfig)
                self.buyCloud(projConfig)
                doPush(cloud)
            else :
                self.log.writeToLog(self.errorCodes['4150'], [self.pid, self.getCloudOwner(cloud)])
        else :
            if force :
                self.setCloudPushTime(projConfig)
                doPush(cloud)
            else :
                if self.isNewerThanCloud(cloud, projConfig) :
                    self.setCloudPushTime(projConfig)
                    doPush(cloud)
                else :
                    self.log.writeToLog(self.errorCodes['4160'], [self.pid])


    def pullFromCloud (self, force = False, tPath = None) :
        '''Pull data from cloud storage and merge/replace local data.
        Do a full backup first before starting the actual pull operation.'''

        # Make the cloud reference
        cloud = os.path.join(self.tools.resolvePath(self.userConfig['Resources']['cloud']), self.pid)
        # Make the project home reference
        if tPath :
            if self.tools.resolvePath(tPath) :
                tPath = self.tools.resolvePath(tPath)
                lastFolder = os.path.basename(tPath)
                if lastFolder == self.pid :
                    projHome = tPath
                else :
                    projHome = os.path.join(tPath, self.pid)
            else :
                self.log.writeToLog(self.errorCodes['4220'], [tPath])
        elif self.projHome :
            projHome = self.projHome
        else :
            projHome = self.tools.resolvePath(os.path.join(self.userConfig['Resources']['projects'], self.pid))

        def doPull () :
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
                    elif self.tools.isOlder(pFile, cFile) :
                        if os.path.isfile(pFile) :
                            os.remove(pFile)
                        shutil.copy(cFile, pFile)
                        cr +=1
            # Report what happened
            self.log.writeToLog(self.errorCodes['4210'])
            if cn == 0 and cr == 0 :
                self.log.writeToLog(self.errorCodes['4120'])
            else :
                if cn > 0 :
                    self.log.writeToLog(self.errorCodes['4130'], [str(cn)])
                if cr > 0 :
                    self.log.writeToLog(self.errorCodes['4140'], [str(cr)])

        # This is a new project to this system
        if not os.path.exists(projHome) :
            shutil.copytree(cloud, projHome)
            self.registerProject(projHome)
            self.log.writeToLog(self.errorCodes['4270'], [self.pid,self.getLocalOwner()])
        # For anything else more testing will be needed
        else :
            if force :
                doPull()
                self.buyLocal(self.getConfig(projHome))
            else :
                if self.sameOwner(cloud) :
                    if self.isNewerThanLocal(cloud, self.getConfig(projHome)) :
                        doPull()
                    else :
                        self.log.writeToLog(self.errorCodes['4260'], [self.pid])
                else :
                    self.log.writeToLog(self.errorCodes['4250'], [self.pid, self.getCloudOwner(cloud)])




