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
from rapuma.core.tools import *


class ProjBackup (object) :

    def __init__(self, local) :
        '''Intitate the whole class and create the object.'''

        self.local          = local
        print dir(local)


    ###############################################################################
    ########################## Archive Project Functions ##########################
    ###############################################################################

    def makeExcludeFileList (self) :
        '''Return a list of files that are not necessary to be included in a backup
        template or an archive. These will be all auto-generated files that containe system-
        specific paths, etc.'''

        excludeFiles = []
        excludeTypes = ['.delayed', '.log', '.parlocs', '.pdf', '.tex', '.piclist', '.adj']

        # Work out from the component type what the settings file names are
        for cType in aProject.projConfig['CompTypes'].keys() :
            rndr = aProject.projConfig['CompTypes'][cType]['renderer']
            aProject.createManager(cType.lower(), rndr)
            excludeFiles.append(aProject.managers[cType.lower() + '_' + rndr.capitalize()].macLinkFile)
            excludeFiles.append(aProject.managers[cType.lower() + '_' + rndr.capitalize()].setFileName)

        # Now add to the list all the .tex files that are associated with components
        for cName in aProject.projConfig['Components'].keys() :
            # Need to create component obj. (Is there a better way?)
            aProject.createComponent(cName)
            # Sort out cid types
            if aProject.components[cName].getUsfmCid(cName) :
                for t in excludeTypes :
                    cidFile = os.path.join(aProject.local.projComponentsFolder, cName, aProject.components[cName].getUsfmCid(cName) + t)
                    if os.path.isfile(cidFile) :
                        excludeFiles.append(aProject.components[cName].getUsfmCid(cName) + t)
            # Sort out cName types
            for t in excludeTypes :
                cNameFile = os.path.join(aProject.local.projComponentsFolder, cName, cName + t)
                if os.path.isfile(cNameFile) :
                    excludeFiles.append(cName + t)

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
        excludeFiles = makeExcludeFileList(aProject)

        zipUpProject(aProject.local.projHome, archTarget, excludeFiles)

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


    def zipUpProject (self, source, target = None, excludeFiles = None) :
        '''Zip up a project and deposit it to target location. Be sure to strip
        out all all auto-created, user-specific files that could mess up a
        transfer to another system. This goes for archives and backups'''

        # Do the zip magic here
        # First list some types we don't want to include in our archive
        if not excludeFiles :
            excludeFiles = []
    #    excludeType = ['.delayed', '.log', '.parlocs', '.pdf']
    #    # Now list the full file names of any excptions to the above type exclusions
    #    excludeException = ['rapuma.log']
        root_len = len(source)
        with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as myzip :
            for root, dirs, files in os.walk(source):
                # Chop off the part of the path we do not need to store
                zip_root = os.path.abspath(root)[root_len:]
                for f in files:
                    if f in excludeFiles :
                        continue
                    if not f[-1] == '~' :
                        fn, fx = os.path.splitext(f)
    #                    if not fx in excludeType or f in excludeException :
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

    def backupProject (self, pid) :
        '''Backup a project. Send the compressed backup file to the user-specified
        backup folder. If none is specified, put the archive in cwd. If a valid
        path is specified, send it to that location. This is a very simplified
        backup so it will only keep one copy in any given location. If another
        copy exists, it will overwrite it.'''

        # Check to see if the pid is valid in the system (it has to be)
        isProject(pid)
        projHome = uc.userConfig['Projects'][pid]['projectPath']
        aProject = initProject(pid)

        # Set some paths and file names
        backupName = pid + '.zip'
        userBackups = uc.userConfig['Resources']['backups']
        backupTarget = ''
        if os.path.isdir(userBackups) :
            backupTarget = os.path.join(userBackups, backupName)
        else :
            terminal('\nError: User backup storage path not yet configured!\n')
            dieNow()

        # Get a list of files we don't want
        excludeFiles = makeExcludeFileList(aProject)

        zipUpProject(projHome, backupTarget, excludeFiles)

        # Finish here
        terminal('Backup for [' + pid + '] created and saved to: ' + backupTarget + '\n')


    def restoreBackup (self, pid) :
        '''Restore a project from the user specified storage area. If that
        is not set, it will look for the backup (pid.zip) in cwd. Use path to
        specify where the project will be restored. Rapuma will register the project
        there. Otherwise, it will restore to cwd and register it there.'''

        # Check to see if the user included the extention
        try :
            pid.split('.')[1] == 'zip'
            backName = pid
            pid = pid.split('.')[0]
        except :
            backName = pid + '.zip'

        # Check to see if the pid is valid in the system (it has to be)
        isProject(pid)
        projHome = uc.userConfig['Projects'][pid]['projectPath']

        # Check to see if the archive exsists
        try :
            if os.path.isdir(uc.userConfig['Resources']['backups']) :
                backup = os.path.join(uc.userConfig['Resources']['backups'], backName)
        except :
            terminal('\nError: The path (or name) given is not valid: [' + backup + ']\n')
            dieNow()

        # Make the exsiting project a temp backup in case something goes wrong
        if os.path.isdir(projHome) :
            # Remove old backup-backup
            if os.path.isdir(projHome + '.bak') :
                shutil.rmtree(projHome + '.bak')
            # Make a fresh copy of the backup-backup
            shutil.copytree(projHome, projHome + '.bak')

        # If we made it this far, extract the archive
        with zipfile.ZipFile(backup, 'r') as myzip :
            myzip.extractall(projHome)

        # Permission for executables is lost in the zip, fix it here
        for folder in ['Scripts', os.path.join('Macros', 'User')] :
            fixExecutables(os.path.join(projHome, folder))

        # Finish here (We will leave the backup-backup in place)
        terminal('\nRapuma backup [' + pid + '] has been restored to: ' + projHome + '\n')


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
        excludeFiles = makeExcludeFileList(aProject)

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


    def pushToCloud (self, pid) :
        '''Push local project data to the cloud. If a file in the cloud is
        older than the project file, it will be sent. Otherwise, it will
        be skipped.'''

        aProject            = initProject(pid)
        projHome            = uc.userConfig['Projects'][pid]['projectPath']
        local               = ProjLocal(rapumaHome, userHome, projHome)
        cloud               = os.path.join(uc.userConfig['Resources']['cloud'], pid)

        # Make a cloud
        if not os.path.isdir(cloud) :
            os.makedirs(cloud)

        # Get a list of files we do not want
        excludeFiles        = makeExcludeFileList(aProject)

        # Get a total list of files from the project
        cn = 0
        cr = 0
        for folder, subs, files in os.walk(projHome):
            for fileName in files:
                if fileName not in excludeFiles :
                    if not os.path.isdir(folder.replace(projHome, cloud)) :
                        os.makedirs(folder.replace(projHome, cloud))
                    cFile = os.path.join(folder, fileName).replace(projHome, cloud)
                    pFile = os.path.join(folder, fileName)
                    if fileName[-1] == '~' :
                        continue
                    elif not os.path.isfile(cFile) :
                        shutil.copy(pFile, cFile)
                        cn +=1
                    elif isOlder(pFile, cFile) :
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



