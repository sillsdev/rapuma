#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will create an object that will hold all the general local info
# files and folders in the Rapuma system and for a given project.


###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, site, platform

# Load the local classes
from rapuma.core.tools              import Tools
from rapuma.core.user_config        import UserConfig


class ProjLocal (object) :

    def __init__(self, pid, gid = None, cType = 'usfm', mType = 'book', macPack = 'usfmTex') :
        '''Intitate a class object which contains all the project file folder locations.
        The files and folders are processed by state. If the system is in a state where
        certain parent files or folders do not exist, the child file or folder will be
        set to None. This should only cause problems when certain proecess are attempted
        that should not be given a particular state. For example, a render process should
        fail if a group/component was never added.'''

        self.tools              = Tools()
        self.pid                = pid
        self.gid                = gid
        self.rapumaHome         = os.environ.get('RAPUMA_BASE')
        self.userHome           = os.environ.get('RAPUMA_USER')
        self.osPlatform         = platform.architecture()[0][:2]
        self.user               = UserConfig()
        self.userConfig         = self.user.userConfig
        self.userResource       = os.path.join(site.USER_BASE, 'share', 'rapuma')
        self.projHome           = os.path.join(os.path.expanduser(self.userConfig['Resources']['projects']), self.pid)
        self.projFolders        = []
        self.localDict          = None
        self.cType              = cType
        self.mType              = mType
        self.macPack            = macPack
        debug                   = self.userConfig['System']['debugging']
        debugOutput             = os.path.join(self.userResource, 'debug', 'local_path.log')
        if debug and not os.path.exists(os.path.join(self.userResource, 'debug')) :
            os.makedirs(os.path.join(self.userResource, 'debug'))

        # Bring in all the Rapuma default project location settings
        rapumaXMLDefaults = os.path.join(self.rapumaHome, 'config', 'proj_local.xml')
        if os.path.exists(rapumaXMLDefaults) :
            self.localDict = self.tools.xmlFileToDict(rapumaXMLDefaults)
        else :
            raise IOError, "Can't open " + rapumaXMLDefaults

        # Create the user resources dir under .local/share
        if not os.path.isdir(self.userResource) :
            os.makedirs(self.userResource)

        # Troll through the localDict and create the file and folder defs we need
        if debug :
            debugObj = codecs.open(debugOutput, "w", encoding='utf_8')
        for sections in self.localDict['root']['section'] :
            for section in sections :
                secItems = sections[section]
                if type(secItems) is list :
                    for item in secItems :
                        if item.has_key('folderID') :
                            # First make a folder name placeholder and set 
                            # to None if it doesn't exist already
                            try :
                                getattr(self, str(item['folderID']))
                            except :
                                setattr(self, item['folderID'], None)
                            # Next, if the 'relies' exists, set the value
                            val = self.processNestedPlaceholders(item['folderPath'])
                            # Check for relative path and fix it if needed
                            if len(val) > 0 :
                                if val[0] == '~' :
                                    val = os.path.expanduser(val)
                            if item['relies'] :
                                if getattr(self, item['relies']) :
                                    setattr(self, item['folderID'], val)
                                    self.projFolders.append(val)
                                    if debug :
                                        debugObj.write(item['folderID'] + ' = ' + val + '\n')
                            else :
                                setattr(self, item['folderID'], val)
                                if debug :
                                    debugObj.write(item['folderID'] + ' = ' + val + '\n')
                        elif item.has_key('fileID') :
                            # First make a file name placeholder and set 
                            # to None if it doesn't exist already
                            try :
                                getattr(self, str(item['fileID']))
                                getattr(self, str(item['fileID'] + 'Name'))
                            except :
                                setattr(self, item['fileID'], None)
                                setattr(self, item['fileID'] + 'Name', None)
                            # Get the two values we need
                            valName = self.processNestedPlaceholders(item['fileName'])
                            valPath = self.processNestedPlaceholders(item['filePath'])
                            if item['relies'] :
                                if getattr(self, item['relies']) :
                                    setattr(self, item['fileID'] + 'Name', valName)
                                    setattr(self, item['fileID'], os.path.join(valPath, valName))
                                    if debug :
                                        debugObj.write(item['fileID'] + 'Name = ' + valName + '\n')
                                        debugObj.write(item['fileID'] + ' = ' + getattr(self, item['fileID']) + '\n')
                            else :
                                setattr(self, item['fileID'] + 'Name', valName)
                                setattr(self, item['fileID'], os.path.join(valPath, valName))
                                if debug :
                                    debugObj.write(item['fileID'] + 'Name = ' + valName + '\n')
                                    debugObj.write(item['fileID'] + ' = ' + getattr(self, item['fileID']) + '\n')

        # Add configuation file names
        configFiles = ['project', 'adjustment', 'layout', 'illustration', 'font']
        # Create placeholders for basic conf file names
        for cf in configFiles :
            setattr(self, cf + 'ConfFile', None)
        # Add the real settings if we can
        if self.projHome :
            for cf in configFiles :
                # Set the config path/file value
                setattr(self, cf + 'ConfFileName', cf + '.conf')
                if debug :
                    debugObj.write(cf + 'ConfFileName' + ' = ' + getattr(self, cf + 'ConfFileName', cf + '.conf') + '\n')
                setattr(self, cf + 'ConfFile', os.path.join(self.projConfFolder, cf + '.conf'))
                if debug :
                    debugObj.write(cf + 'ConfFile' + ' = ' + getattr(self, cf + 'ConfFile', cf + '.conf') + '\n')
                # Set the xml config file name (project is according to media type)
                if cf == 'project' :
                    setattr(self, cf + 'ConfXmlFileName', self.mType + '.xml')
                    if debug :
                        debugObj.write(cf + 'ConfXmlFileName' + ' = ' + getattr(self, cf + 'ConfXmlFileName', self.mType + '.xml') + '\n')
                elif cf == 'layout' :
                    setattr(self, cf + 'ConfXmlFileName', self.mType + '_layout.xml')
                    if debug :
                        debugObj.write(cf + 'ConfXmlFileName' + ' = ' + getattr(self, cf + 'ConfXmlFileName', self.mType + '_layout.xml') + '\n')
                else :
                    setattr(self, cf + 'ConfXmlFileName', cf + '.xml')
                    if debug :
                        debugObj.write(cf + 'ConfXmlFileName' + ' = ' + getattr(self, cf + 'ConfXmlFileName', cf + '.xml') + '\n')
                # Set the full path/file value
                setattr(self, cf + 'ConfXmlFile', os.path.join(self.rapumaConfigFolder, getattr(self, cf + 'ConfXmlFileName')))
                if debug :
                    debugObj.write(cf + 'ConfXmlFileName' + ' = ' + getattr(self, cf + 'ConfXmlFile', os.path.join(self.rapumaConfigFolder, getattr(self, cf + 'ConfXmlFileName'))) + '\n')

        # Add macPack files via a specific macPack XML configuation file
        if self.macPack and os.path.exists(self.macPackConfXmlFile) :
            macPackDict = self.tools.xmlFileToDict(self.macPackConfXmlFile)
            macPackFilesDict = {}
            for sections in macPackDict['root']['section'] :
                if sections['sectionID'] == 'Files' :
                    for section in sections :
                        secItem = sections[section]
                        if type(secItem) is list :
                            for f in secItem :
                                macPackFilesDict[f['moduleID']] = self.processNestedPlaceholders(f['fileName'])
            for f in macPackFilesDict.keys() :
                setattr(self, f, macPackFilesDict[f])
                if debug :
                    debugObj.write(f + ' = ' + getattr(self, f) + '\n')

        # Close the debug file if we need to
        if debug :
            debugObj.close()

        # Set Rapuma User config file name (already defined in user_config)
        self.userConfFileName           = self.user.userConfFileName
        self.userConfFile               = self.user.userConfFile
        # Add log file names
        if self.projHome :
            self.projLogFileName        = 'rapuma.log'
            self.projLogFile            = os.path.join(self.projHome, self.projLogFileName)
            self.projErrorLogFileName   = 'error.log'
            self.projErrorLogFile       = os.path.join(self.projHome, self.projErrorLogFileName)
        # Other info vals to set
        self.lockExt                    = '.lck'

        # Do some cleanup like getting rid of the last sessions error log file.
        try :
            if os.path.isfile(self.projErrorLogFile) :
                os.remove(self.projErrorLogFile)
        except :
            pass


###############################################################################
############################### Local Functions ###############################
###############################################################################

    def processNestedPlaceholders (self, line) :
        '''Search a string (or line) for a type of Rapuma placeholder and
        insert the value.'''

        result = []
        end_of_previous_segment = 0
        for (ph_start, ph_end) in self.getPlaceHolder(line) :
            unchanged_segment = line[end_of_previous_segment:ph_start]
            result.append(unchanged_segment)
            ph_text = line[ph_start+1:ph_end]
            replacement = self.processNestedPlaceholders(ph_text)
            result.append(unicode(replacement))
            end_of_previous_segment = ph_end+1  # Skip the closing bracket
        result.append(line[end_of_previous_segment:])
        resultline = "".join(result)
        result_text = self.processSinglePlaceholder(resultline)
        return result_text


    def processSinglePlaceholder (self, ph) :
        '''Once we are sure we have a single placeholder (noting embedded) this
        will process it and replace it with the correct value.'''

        holderType = ph.split(':')[0]
        try :
            holderKey = ph.split(':')[1]
        except :
            holderKey = ''

        result = ph # If nothing matches below, default to returning placeholder unchanged

        # The following placeholders are supported
        if holderType == 'pathSep' :
            result = os.sep
        elif holderType == 'self' :
            result = getattr(self, holderKey)
        elif holderType == 'config' :
            result = self.getConfigValue(holderKey)

        return result


    def hasPlaceHolder (self, line) :
        '''Return True if this line has a data place holder in it.'''

        # If things get more complicated we may need to beef this up a bit
        if line.find('[') > -1 and line.find(']') > -1 :
            return True


    def getConfigValue (self, val, default=None) :
        '''Return the value from a config function or return default value if key not found.'''

        keyparts = val.split('|')
        curval = getattr(self, keyparts[0], None)
        if curval is None: return default
        for key in keyparts[1:]:
            curval = curval.get(key, None)
            if curval is None: return default
        return curval



    def getPlaceHolder (self, line) :
        '''Return place holder type and a key if one exists from a TeX setting line.
        Pass over the line and return (yield) each placeholder found.'''

        nesting_level = 0
        remembered_idx = None
        for idx, ch in enumerate(line):
            if ch == '[':
                nesting_level += 1
                if remembered_idx is None:
                    remembered_idx = idx
            elif ch == ']':
                nesting_level -= 1
                if nesting_level <= 0:
                    found_idx = remembered_idx
                    remembered_idx = None
                    yield (found_idx, idx)


    def getComponentFiles (self, gid, cid, cType=None) :
        '''Return a dictionary that contains files and paths for a set
        of component files. The path/names are only theoretical and
        need to be tested by the calling function. However, in the case
        of the source name, it will be a null item if the file does not
        exist.'''

#        import pdb; pdb.set_trace()

        if cType :
            self.cType = cType
        files               = {}
        compFolder          = os.path.join(self.projComponentFolder, cid)
        # Handle USFM text special
        if self.cType == 'usfm' :
            # These are predictable
            fileHandle          = cid + '_base'
            files['working']    = os.path.join(compFolder, fileHandle + '.' +  self.cType)
            files['backup']     = files['working'] + '.cv1'
            # Source file may not exist so we will try to find it
            try :
                # Since the source name is not predictable we will look for a
                # file with a .source extention and assume that is it. If not
                # found we leave the source item empty
                fileList = os.listdir(compFolder)
                for f in fileList :
                    if f.find('.source') > 0 :
                        files['source'] = os.path.join(compFolder, f)
            except :
                files['source'] = None
        else :
            files['working']    = os.path.join(compFolder, cid + '.' +  self.cType)
            files['backup']     = files['working'] + '.bak'
        
        # Return the dictionary
        return files



