#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (sparkycbr at gmail dot com)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle project backup/archive operations.

###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, zipfile, shutil, re, sys, tempfile
from configobj import ConfigObj

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.core.user_config        import UserConfig
from rapuma.core.proj_local         import ProjLocal
from rapuma.core.proj_log           import ProjLog
from rapuma.manager.project         import Project
from rapuma.project.proj_config     import Config
from rapuma.project.proj_commander  import ProjCommander


class ProjData (object) :

    def __init__(self, pid, gid = None) :
        '''Intitate the whole class and create the object.'''

        self.pid            = pid
        self.gid            = gid
        self.tools          = Tools()
        self.user           = UserConfig()
        self.userConfig     = self.user.userConfig
        self.local          = ProjLocal(pid)
        self.log            = ProjLog(pid)
        self.projHome       = os.path.join(os.path.expanduser(self.userConfig['System']['projects']), self.pid)
        self.projList       = self.tools.getProjIdList(os.path.expanduser(self.userConfig['System']['projects']))

        # Log messages for this module
        self.errorCodes     = {

            '1220' : ['LOG', 'Project [<<1>>] already registered in the system.'],
            '1240' : ['ERR', 'Could not find/open the Project configuration file for [<<1>>]. Project could not be registered!'],

            '3410' : ['LOG', 'Backup file cull skipping: [<<1>>] Not a recognized Rapuma backup file name format.'],
            '3510' : ['ERR', 'The path (or name) given is not valid: [<<1>>].'],
            '3530' : ['MSG', 'Project backup: [<<1>>] has been restored to: [<<2>>]. A backup of the orginal project remains and must be manually removed.'],
            '3550' : ['ERR', 'Project backup version request: [<<1>>] exceeds the maxium number which could be in storage which is: [<<2>>]. Request an earlier (lesser) version.'],
            '3610' : ['ERR', 'The [<<1>>]. project is not registered. No backup was done.'],
            '3620' : ['ERR', 'The path to the backup folder is not valid [<<1>>]. Please try again.'],
            '3622' : ['ERR', 'The path to the backup folder is not set. Please set it and try again.'],
            '3625' : ['ERR', 'The path given to the backup folder is not valid [<<1>>]. Please set the system backup path.'],
            '3630' : ['MSG', 'Backup for [<<1>>] created and saved to: [<<2>>]'],

            '4110' : ['MSG', 'Completed merging data.'],
            '4120' : ['MSG', 'No files updated.'],
            '4130' : ['MSG', 'Added: <<1>> file(s).'],
            '4140' : ['MSG', 'Updated: <<1>> file(s)'],
            '4150' : ['WRN', 'The project data in: [<<1>>] will be replaced with the data from: [<<2>>].'],

            '4210' : ['MSG', 'Completed pulling/restoring data from the cloud.'],
            '4220' : ['ERR', 'Cannot resolve path: [<<1>>]'],
            '4250' : ['ERR', 'The cloud project [<<1>>] you want to pull from is owned by [<<2>>]. Use force (-f) to pull the project and change the local owner ID.'],
            '4260' : ['ERR', 'The local project [<<1>>] is newer than the cloud copy. If you seriously want to overwrite it, use force (-f) to do so.'],
            '4270' : ['MSG', 'Restored the project [<<1>>] from the cloud copy. Local copy is owned by [<<2>>].'],

        }


###############################################################################
############################## General Functions ##############################
###############################################################################
####################### Error Code Block Series = 1000 ########################
###############################################################################



###############################################################################
########################## Archive Project Functions ##########################
###############################################################################
####################### Error Code Block Series = 2000 ########################
###############################################################################

    def makeExcludeFileList (self, source) :
        '''Return a list of files that are not necessary to be included in a backup
        template or an archive. These will be all auto-generated files that containe system-
        specific paths, etc.'''

        excludeFiles        = []
        excludeTypes        = ['delayed', 'log', 'notepages', 'parlocs', 'pdf', 'tex', 'piclist', 'adj', 'zip']
        excludeFolders      = ['Draft', 'Final', 'HelperScript', 'Proof']

        # Process the excluded folders
        for root, dirs, files in os.walk(source) :
            for fileName in files :
                if os.path.basename(root) in excludeFolders :
                    excludeFiles.append(os.path.join(root, fileName))
                else :
                    # Get rid of edited backup files
                    if fileName[-1] == '~' :
                        excludeFiles.append(os.path.join(root, fileName))
                        continue
                    ext = os.path.splitext(fileName)[1][1:]
                    if ext in excludeTypes :
                        # A special indicator for file we want to keep
                        if fileName.find('-ext.') > 0 :
                            continue

        return excludeFiles

# FIXME: Should archiveProject() use self.pid instead of explicitly passing in a pid?
    #def archiveProject (self, pid, path = None) :
        #'''Archive a project. Send the compressed archive file to the user-specified
        #archive folder. If none is specified, put the archive in cwd. If a valid
        #path is specified, send it to that location. Like backup, this too will
        #overwrite any existing file of the same name. The difference is that this
        #will also disable the project so it cannot be accesses by Rapuma. When a
        #project is archived, all work should cease on the project.'''

        ## Make a private project object just for archiving
        #aProject = Project(pid, self.gid)
        ## Set some paths and file names
        #archName = aProject.projectIDCode + '.rapuma'
        #userArchives = self.userConfig['Resources']['archive']
        #archTarget = ''
        #if path :
            #path = self.tools.resolvePath(path)
            #if os.path.isdir(path) :
                #archTarget = os.path.join(path, archName)
            #else :
                #self.tools.terminal('\nError: The path given is not valid: [' + path + ']\n')
                #self.tools.dieNow()
        #elif os.path.isdir(userArchives) :
            #archTarget = os.path.join(userArchives, archName)
        #elif os.path.isdir(os.path.dirname(aProject.local.projHome)) :
            ## Default to the dir just above the project
            #archTarget = os.path.dirname(aProject.local.projHome)
        #else :
            #self.tools.terminal('\nError: Cannot resolve a path to create the archive file!\n')
            #self.tools.dieNow()

        ## Get a list of files we don't want
        #excludeFiles = self.makeExcludeFileList(source)

        #self.zipUpProject(archTarget, excludeFiles)

        ## Rename the source dir to indicate it was archived
        #bakArchProjDir = aProject.local.projHome + '(archived)'
        #if os.path.isdir(bakArchProjDir) :
            #self.tools.terminal('\nError: Cannot complete archival process!\n')
            #self.tools.terminal('\nAnother archived version of this project exsits with the folder name of: ' + self.tools.fName(bakArchProjDir) + '\n')
            #self.tools.terminal('\nPlease remove or rename it and then repete the process.\n')
            #self.tools.dieNow()
        #else :
            #os.rename(aProject.local.projHome, bakArchProjDir)

        ## Finish here
        #self.tools.terminal('Archive for [' + pid + '] created and saved to: ' + archTarget + '\n')


    def zipUpProject (self, target, excludeFiles = None) :
        '''Zip up a project and deposit it to target location. Be sure to strip
        out all all auto-created, user-specific files that could mess up a
        transfer to another system. This goes for archives and backups'''

#        import pdb; pdb.set_trace()

        # In case an exclude list is not given
        if not excludeFiles :
            excludeFiles = []

        # Do the zip magic here
        root_len = len(self.local.projHome)
        with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as myzip :
            sys.stdout.write('Backing up files')
            sys.stdout.flush()
            for root, dirs, files in os.walk(self.local.projHome) :
                # Chop off the part of the path we do not need to store
                zip_root = os.path.abspath(root)[root_len:]
                for f in files :
                    if os.path.join(root, f) in excludeFiles :
                        continue
                    if not f[-1] == '~' :
                        fn, fx = os.path.splitext(f)
                        fullpath = os.path.join(root, f)
                        zip_name = os.path.join(zip_root, f)
                        sys.stdout.write('.')
                        sys.stdout.flush()
                        myzip.write(fullpath, zip_name, zipfile.ZIP_DEFLATED)
            # Add a space before the next message
            print '\n'

# FIXME: Should restoreArchive() use self.pid instead of explicitly passing in a pid?
    #def restoreArchive (self, pid, targetPath, sourcePath = None) :
        #'''Restore a project from the user specified storage area or sourcePath if 
        #specified. Use targetPath to specify where the project will be restored.
        #Rapuma will register the project there.'''

        ## Check to see if the user included the extension
        #try :
            #pid.split('.')[1] == 'rapuma'
            #archName = pid
            #pid = pid.split('.')[0]
        #except :
            #archName = pid + '.rapuma'

        #archSource = ''
        #archTarget = ''
        #userArchives = ''

        ## First look for the archive that is to be restored
        #if sourcePath :
            #if os.path.isdir(sourcePath) :
                #archSource = os.path.join(sourcePath, archName)
        #elif os.path.isdir(self.userConfig['Resources']['archive']) :
            #userArchives = self.userConfig['Resources']['archive']
            #archSource = os.path.join(userArchives, archName)
        #else :
            #self.tools.terminal('\nError: The path (or name) given is not valid: [' + archSource + ']\n')
            #self.tools.dieNow()

        ## Now set the target params
        #if targetPath :
            #if not os.path.isdir(targetPath) :
                #self.tools.terminal('\nError: The path given is not valid: [' + targetPath + ']\n')
                #self.tools.dieNow()
            #else :
                #archTarget = os.path.join(targetPath, pid)

        ## If we made it this far, extract the archive
        #with zipfile.ZipFile(archSource, 'r') as myzip :
            #myzip.extractall(archTarget)

        ## Permission for executables is lost in the zip, fix it here
        #for folder in ['Scripts', os.path.join('Macros', 'User')] :
            #self.tools.fixExecutables(os.path.join(archTarget, folder))

## FIXME: This will need some work 

        ## Add project to local Rapuma project registry
        ## To do this we need to open up the restored project config file
        ## and pull out some settings.
        #local       = ProjLocal(pid)
        #pc          = Config(pid)
        #log         = ProjLog(pid)
        #aProject    = Project(pid, self.gid)
    ##    import pdb; pdb.set_trace()

        ## Finish here
        #self.tools.terminal('\nRapuma archive [' + pid + '] has been restored to: ' + archTarget + '\n')


###############################################################################
########################### Backup Project Functions ##########################
###############################################################################
####################### Error Code Block Series = 3000 ########################
###############################################################################

    def cullBackups (self, maxBak, bakDir) :
        '''Remove any excess backups from the backup folder in
        this project.'''

        # Get number of maximum backups to store
        maxStoreBackups = int(maxBak)
        if not maxStoreBackups or maxStoreBackups == 0 :
            maxStoreBackups = 1

        # Build the cullList
        cullList = []
        files = os.listdir(bakDir)
        for f in files :
            try :
                cullList.append(int(f.split('.')[0]))
            except :
                self.log.writeToLog(self.errorCodes['3410'], [f])
        # Remove oldest file(s)
        while len(cullList) > maxStoreBackups :
            fn = min(cullList)
            cullList.remove(min(cullList))
            os.remove(os.path.join(bakDir, str(fn) + '.zip'))


    def backupProject (self, targetPath=None) :
        '''Backup a project. Send the compressed backup file with a date-stamp
        file name to the user-specified backup folder. If a target path is 
        specified, put the archive there but use the PID in the name. If other
        backups with the same name exist there, increment with a number.'''

        # First see if this is even a valid project
        if self.pid not in self.projList :
            self.log.writeToLog(self.errorCodes['3610'], [self.pid])

        # Set some paths and file names
        if not targetPath :
            # Now check for a valid location to backup to
            if self.local.userLibBackup == '' :
                self.log.writeToLog(self.errorCodes['3622'])
            elif not os.path.exists(self.local.userLibBackup) :
                self.log.writeToLog(self.errorCodes['3620'], [self.local.userLibBackup])
            projBackupFolder    = os.path.join(self.local.userLibBackup, self.pid)
            backupTarget        = os.path.join(projBackupFolder, self.tools.fullFileTimeStamp() + '.zip')
        else :
            projBackupFolder    = self.tools.resolvePath(targetPath)
            # Now check for a valid target path
            if not os.path.exists(projBackupFolder) :
                self.log.writeToLog(self.errorCodes['3625'], [targetPath])
            backupTarget        = self.tools.incrementFileName(os.path.join(projBackupFolder, self.pid + '.zip'))

        # Make sure the dir is there
        if not os.path.exists(projBackupFolder) :
            os.makedirs(projBackupFolder)

#        import pdb; pdb.set_trace()

        # Zip up but use a list of files we don't want
        self.zipUpProject(backupTarget, self.makeExcludeFileList(source))

        # Cull out any excess backups
        if not targetPath :
            self.cullBackups(self.userConfig['System']['maxStoreBackups'], projBackupFolder)

        # Finish here
        pc = Config(self.pid)
        pc.getProjectConfig()
        pc.projectConfig['Backup']['lastBackup'] = self.tools.fullFileTimeStamp()
        self.tools.writeConfFile(pc.projectConfig)
        self.log.writeToLog(self.errorCodes['3630'], [self.pid,backupTarget])
        return True


    def backupRestore (self, backup, target = None) :
        '''Restore a backup to the current or specified project.'''

#        import pdb; pdb.set_trace()

        if not target :
            target = self.local.projHome

        # Now remove the orginal
        if os.path.exists(target) :
            shutil.rmtree(target)
        # Create an empty folder to restore to
        os.makedirs(target)

        # If we made it this far, extract the archive
        with zipfile.ZipFile(backup, 'r') as myzip :
            myzip.extractall(target)
        return True


#    def restoreLocalBackup (self, bakFile) :
#        '''Restore from a project backup. As a project may have multiple backups in
#        its backup folder, the user will need to provide a number from 1 to n (n being
#        the number of backups in the folder, 1 being the most recent and n being the
#        oldest). If no number is provided, 1, (the most recent) will be restored.'''

#        # Adjust bNum if needed
#        maxBak = int(self.userConfig['System']['maxStoreBackups'])
#        if not bNum :
#            bNum = 0
#        else :
#            bNum = int(bNum)
#            if bNum <= 0 :
#                bNum = 0
#            elif bNum > maxBak :
#                self.log.writeToLog(self.errorCodes['3550'], [str(bNum), str(maxBak)])
#            else :
#                bNum = bNum-1

#        # Get vals we need
#        projHome            = self.getProjHome()
#        projBackupFolder    = self.tools.resolvePath(os.path.join(self.userConfig['Resources']['backup'], self.pid))

#        # Get the archive file name
#        files = os.listdir(projBackupFolder)
#        fns = []
#        for f in files :
#            fns.append(int(f.split('.')[0]))
#        # Sort the list, last (latest) first
#        fns.sort(reverse=True)
#        # Make file path/name
#        backup = os.path.join(projBackupFolder, str(fns[bNum]) + '.zip')
#        if not os.path.exists(backup) :
#            self.log.writeToLog(self.errorCodes['3510'], [backup])

#        # Restore the backup
#        self.backupRestore(backup, projHome)

#        # Permission for executables is lost in the zip, fix them here
#        self.tools.fixExecutables(projHome)

#        # Add helper scripts if needed
#        if self.tools.str2bool(self.userConfig['System']['autoHelperScripts']) :
#            ProjCommander(self.pid).updateScripts()

#        # Finish here (We will leave the project backup in place)
#        self.log.writeToLog(self.errorCodes['3530'], [self.tools.fName(backup),projHome])


    def restoreExternalBackup (self, source, target = None, force = False) :
        '''Restore a non-existant project from an external backup to a target folder.
        If no target is provided the project will be installed in the default project
        folder. The source path and ZIP file must be valid'''

        # Get/make the (localized) project home reference
        projHome = self.getProjHome(target)

#        import pdb; pdb.set_trace()

        # Create the source backup file name
#        source = os.path.join(source, self.pid + '.zip')

# FIXME: This needs some review and rework

        # Restore the backup
        if self.backupRestore(source, projHome) :

            # Permission for executables is lost in the zip, fix them here
            self.tools.fixExecutables(projHome)

            # If this is a new project we will need to register it now
            self.registerProject(projHome)

            # Add helper scripts if needed
            if self.tools.str2bool(self.userConfig['System']['autoHelperScripts']) :
                ProjCommander(self.pid).updateScripts()

            # Finish here (We will leave the backup-backup in place)
            self.tools.terminal('\nRapuma backup [' + self.pid + '] has been restored to: ' + projHome + '\n')
            
            return True


###############################################################################
############################ Cloud Backup Functions ###########################
###############################################################################
####################### Error Code Block Series = 4000 ########################
###############################################################################


    def isNewerThanCloud (self, cloud, projectConfig) :
        '''Compare time stamps between the cloud and the local project.
        Return True if the local project is newer or the same age as
        the copy in the cloud. Return True if the project does not
        exist in the local copy of the cloud.'''

        # First see if it exists
        cConfig = self.getConfig(cloud)
        if not cConfig :
            return True
        elif not cConfig.has_key('Backup') :
            return True
        elif not cConfig['Backup'].has_key('lastCloudPush') :
            return True
        # Check local for key
        if not projectConfig.has_key('Backup') :
            return False
        elif not projectConfig['Backup'].has_key('lastCloudPush') :
            return False
        # Compare if we made it this far
        cStamp = cConfig['Backup']['lastCloudPush']
        lStamp = projectConfig['Backup']['lastCloudPush']
        if lStamp >= cStamp :
            return True


    def isNewerThanLocal (self, cloud, projectConfig) :
        '''Compare time stamps between the cloud and the local project.
        Return True if the cloud project is newer or the same age as
        the local copy. Return True if the project does not exist in
        as a local copy.'''

        # First see if the local exists
        if not projectConfig :
            return True

        # See if cloud is there and up-to-date
        cloudConfig = self.getConfig(cloud)
        if not cloudConfig :
            return False

        # Compare if we made it this far
        cStamp = cloudConfig['Backup']['lastCloudPush']
        # It is possible the local has never been pushed
        # If that is the case, local is assumed older
        try :
            pStamp = projectConfig['Backup']['lastCloudPush']
        except :
            return False
        if cStamp >= pStamp :
            return True


    def getConfig (self, projHome) :
        '''Return a valid config object from cloud project.'''

#        import pdb; pdb.set_trace()

        projectConfigFile = os.path.join(projHome, 'Config', 'project.conf')
        if os.path.exists(projectConfigFile) :
            return ConfigObj(projectConfigFile, encoding='utf-8')


    def getCloudOwner (self, cloud) :
        '''Return the owner of a specified cloud project.'''

        try :
            return self.getConfig(cloud)['Backup']['ownerID']
        except :
            return None


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


    def setCloudPushTime (self, projectConfig) :
        '''Set/reset the lastPush time stamp setting.'''

        projectConfig['Backup']['lastCloudPush'] = self.tools.fullFileTimeStamp()
        self.tools.writeConfFile(projectConfig)


    def buyCloud (self, projectConfig) :
        '''Change the ownership on a project in the cloud by assigning
        your userID to the local project cloudOwnerID. Then, using force
        the next time the project is pushed to the cloud, you will own it.'''

        projOwnerID = self.userConfig['System']['userID']
        projectConfig['Backup']['ownerID'] = projOwnerID
        self.tools.writeConfFile(projectConfig)


    def buyLocal (self, projectConfig) :
        '''Change the ownership on a local project by assigning your
        userID to it.'''

        projOwnerID = self.userConfig['System']['userID']
        projectConfig['Backup']['ownerID'] = projOwnerID
        self.tools.writeConfFile(projectConfig)


    def replaceProject (self, source, target) :
        '''This will completly replace an existing project (target)
        with data from another project (source). This assumes
        source and target are valid.'''

        # We simply just get rid of the target before doing a merge
        shutil.rmtree(target)
        self.log.writeToLog(self.errorCodes['4150'], [target, source])
        self.mergeProjects(source, target)


    def mergeProjects(self, source, target) :
        '''This will merge two Rapuma projects and try to preserve
        data in the target that is newer than the source. This assumes
        target and source are valid.'''
        
        # Get a list of files we do not want
        excludeFiles        = self.makeExcludeFileList(source)

        # Get a total list of files from the project
        cn = 0
        cr = 0
        # Add space for output message
        sys.stdout.write('\n')
        sys.stdout.write('Merging files from: ' + source + ' to: ' + target)
        sys.stdout.flush()
        for folder, subs, files in os.walk(source):
            for fileName in files:
                # Do not include any backup files we find
                if fileName[-1] == '~' :
                    continue
                if os.path.join(folder, fileName) not in excludeFiles :
                    if not os.path.isdir(folder.replace(source, target)) :
                        os.makedirs(folder.replace(source, target))
                    targetFile = os.path.join(folder, fileName).replace(source, target)
                    sourceFile = os.path.join(folder, fileName)
                    if not os.path.isfile(targetFile) :
                        sys.stdout.write('.')
                        sys.stdout.flush()
                        shutil.copy(sourceFile, targetFile)
                        cn +=1
                    # Otherwise if the cloud file is older than
                    # the project file, refresh it
                    elif self.tools.isOlder(targetFile, sourceFile) :
                        if os.path.isfile(targetFile) :
                            os.remove(targetFile)
                        sys.stdout.write('.')
                        sys.stdout.flush()
                        shutil.copy(sourceFile, targetFile)
                        cr +=1
        # Add space for next message
        sys.stdout.write('\n')


        # Report what happened
        self.log.writeToLog(self.errorCodes['4110'])
        if cn == 0 and cr == 0 :
            self.log.writeToLog(self.errorCodes['4120'])
        else :
            if cn > 0 :
                self.log.writeToLog(self.errorCodes['4130'], [str(cn)])
            if cr > 0 :
                self.log.writeToLog(self.errorCodes['4140'], [str(cr)])

        return True


    def getProjHome (self, tPath = None) :
        '''Return a project home path by checking to see what the best path
        might be. Provided path gets first dibs, then '''

        if tPath :
            if os.path.isfile(tPath) :
                return self.local.projHome
            elif self.tools.resolvePath(tPath) :
                tPath = self.tools.resolvePath(tPath)
                lastFolder = os.path.basename(tPath)
                if lastFolder == self.pid :
                    return tPath
                else :
                    return os.path.join(tPath, self.pid)
            else :
                self.log.writeToLog(self.errorCodes['4220'], [tPath])
        elif self.local.projHome :
            return self.local.projHome
        else :
            return self.tools.resolvePath(os.path.join(self.userConfig['System']['projects'], self.pid))



###############################################################################
############################### Template Class ################################
###############################################################################

class Template (object) :

    def __init__(self, pid) :
        '''Intitate the whole class and create the object.'''

        self.pid            = pid
        self.tools          = Tools()
        self.user           = UserConfig()
        self.userConfig     = self.user.userConfig
        self.local          = ProjLocal(pid)
        self.log            = ProjLog(pid)
        self.projData       = ProjData(pid)


    def projectToTemplate (self, tid = None) :
        '''Preserve critical project information in a template. The pid is the project
        that the template will be bassed from. The template will go in the template lib.'''

        # Set needed vals
        if not tid :
            tid             = self.pid
        tempDir             = os.path.join(tempfile.mkdtemp(), tid)
        target              = os.path.join(self.local.userLibTemplate, tid + '.zip')

        # Make a temp copy of the project that we can manipulate
        shutil.copytree(self.local.projHome, tempDir)

        # Now make the config files generic for use with any project
        tc = ConfigObj(os.path.join(tempDir, 'Config', 'project.conf'), encoding='utf-8')
        tc['ProjectInfo']['projectTitle']               = ''
        tc['ProjectInfo']['projectIDCode']              = ''
        tc['ProjectInfo']['projectCreateDate']          = ''
        tc['ProjectInfo']['projectCreateDate']          = ''
        # Remove unnecessary folders
        needNot = ['Component', 'Deliverable', 'Illustration']
        for f in needNot :
            fld = os.path.join(tempDir, f)
            if os.path.exists(fld) :
                shutil.rmtree(fld)
        # Remove unnecessary config files
        needNot = ['adjustment', 'illustration']
        for f in needNot :
            fl = os.path.join(tempDir, 'Config', f + '.conf')
            if os.path.exists(fl) :
                os.remove(fl)
        # Remove unnecessary project config stuff
        needNot = ['Groups', 'Backup']
        for s in needNot :
            if tc.has_key(s) :
                del tc[s]
        # Write out the new template project config file
        tc.filename = os.path.join(tempDir, 'Config', 'project.conf')
        tc.write()

        # Kill the log file
        os.remove(os.path.join(tempDir, 'rapuma.log'))

        # Exclude files
        excludeFiles = self.projData.makeExcludeFileList(source)

        # Zip it up using the above params
        root_len = len(tempDir)
        with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as myzip :
            sys.stdout.write('Creating template')
            sys.stdout.flush()
            for root, dirs, files in os.walk(tempDir):
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
                        sys.stdout.write('.')
                        sys.stdout.flush()
                        myzip.write(fullpath, zip_name, zipfile.ZIP_DEFLATED)

            # Add space for next message
            sys.stdout.write('\n')

        # Remove the temp project dir we made
        self.tools.terminal('\nCompleted creating template: ' + target + '\n')


    def templateToProject (self, targetDir = None, source = None) :
        '''Create a new project based on the provided template ID. If a path to
        the template is not provided it will look in the users template lib. A PID
        must be provided. That is checked with the system. If the same PID is
        found in the system, it must be removed before reruning this function. If
        a non-default location is needed, a target path must be provided.'''

#        import pdb; pdb.set_trace()

        # Set a default target path
        projHome = os.path.join(self.local.projParentDefaultFolder, self.pid)
        # See if we can build a better target path
        if targetDir != '' :
            projHome = os.path.join(targetDir, self.pid)
        elif self.local.projHome :
            projHome = os.path.join(self.local.projHome, self.pid)

#        self.tools.dieNow()

        # Test to see if the project already exists
        if self.pid in self.projList :
            self.tools.terminal('\nError: Project ID [' + self.pid + '] is already exists on this system. Use the remove command to remove it.')
            self.tools.dieNow()
        # Test for source template file
        if not source :
            source = os.path.join(self.local.userLibTemplate, self.pid + '.zip')
            if not os.path.exists(source) :
                self.tools.terminal('\nError: No template can be found for [' + self.pid + ']\n')
                self.tools.dieNow()

        # Unzip the template in place to start the new project
        with zipfile.ZipFile(source, 'r') as myzip :
            myzip.extractall(projHome)

        # Peek into the project
        pc = ConfigObj(os.path.join(projHome, 'Config', 'project.conf'), encoding='utf-8')
        pc['ProjectInfo']['projectCreateDate']         = self.tools.tStamp()
        pc['ProjectInfo']['projectIDCode']             = self.pid
        pc.filename                                    = os.path.join(projHome, 'Config', 'project.conf')
        pc.write()

        # Get the media type from the newly placed project for registration
        projectMediaIDCode = pc['ProjectInfo']['projectMediaIDCode']

        # Reset the local settings
        self.local = ProjLocal(self.pid)

        # Create any folders that might be needed
        for fld in self.local.projFolders :
            folder = os.path.join(self.local.projHome, fld)
            if not os.path.exists(folder) :
                os.makedirs(folder)

        # Report what happened
        self.tools.terminal('A new project [' + self.pid + '] has been created based on the [' + self.tools.fName(source) + '] template.')



