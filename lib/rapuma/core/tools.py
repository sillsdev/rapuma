#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This module will hold all the miscellaneous functions that are shared with
# many other scripts in the system.


###############################################################################
################################## Tools Class ################################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys, re, fileinput, zipfile, shutil, stat
import difflib, tempfile, subprocess
from datetime                               import *
from xml.etree                              import cElementTree as ET
from collections                            import defaultdict
from configobj                              import ConfigObj, Section

###############################################################################
################################ Path Tools Class #############################
###############################################################################

class ToolsPath (object) :
    '''This is a special set of shared path tools.'''

    def __init__(self, pid) :
        '''Do the primary initialization for this manager.'''

        # Rapuma libs
        from rapuma.core.proj_local         import ProjLocal
        from rapuma.project.proj_config     import Config

        self.local                          = ProjLocal(pid)
        self.proj_config                    = Config(pid)
        self.proj_config.getProjectConfig()
        self.projectConfig                  = self.proj_config.projectConfig
        self.pid                            = pid
        self.tools                          = Tools()

###############################################################################
############################ Functions Begin Here #############################
###############################################################################

#    def getSourceFile (self, gid, cid) :
#        '''Get the source file name with path.'''

##        import pdb; pdb.set_trace()

#        # At this time, we only need this right here in this function
#        # Do not bother if there is not source path set
#        if self.local.sourcePath :
#            print 'mmmmmmmmmmmmmmmmmmm'
#            from rapuma.core.paratext import Paratext
#            pt                  = Paratext(self.pid, gid)
#            sourcePath          = self.local.sourcePath
#            cType               = self.projectConfig['Groups'][gid]['cType']
#            sourceEditor        = pt.getSourceEditor()
#            # Build the file name
#            if sourceEditor.lower() == 'paratext' :
#                sName = pt.formPTName(cid)
#            elif sourceEditor.lower() == 'generic' :
#                sName = pt.formGenericName(cid)
#            else :
#                return None

#            return os.path.join(sourcePath, sName)


#    def getWorkingFile (self, gid, cid) :
#        '''Return the working file name with path.'''

#        csid            = self.projectConfig['Groups'][gid]['csid']
#        cType           = self.projectConfig['Groups'][gid]['cType']
#        targetFolder    = os.path.join(self.local.projComponentFolder, cid)
#        return os.path.join(targetFolder, cid + '_' + csid + '.' + cType)


#    def getWorkCompareFile (self, gid, cid) :
#        '''Return the working compare file (saved from last update) name with path.'''

#        return self.getWorkingFile(gid, cid) + '.cv1'


#    def getWorkingSourceFile (self, gid, cid) :
#        '''Get the working source file name with path.'''

#        # Do not bother if no source path exists
#        if self.local.sourcePath :
#            targetFolder    = os.path.join(self.local.projComponentFolder, cid)
#            source          = self.getSourceFile(gid, cid)
#            sName           = os.path.split(source)[1]
#            return os.path.join(targetFolder, sName + '.source')


#    def getGroupPreprocessFile (self, gid) :
#        '''Get the file name and path to the group's preprocess script.'''

#        csid            = self.projectConfig['Groups'][gid]['csid']
#        return os.path.join(self.local.projScriptFolder, csid + '_textPreprocess.py')


###############################################################################
############################ Begin Normal Tools Class #########################
###############################################################################

class Tools (object) :

    def __init__(self) :
        '''Do the primary initialization for this manager.'''


###############################################################################
############################ Functions Begin Here #############################
###############################################################################

    def getPdfPages (self, pdfFile) :
        '''Get the total number of pages in a PDF file.'''

        # Create a temporary file that we will use to hold data.
        # It should be deleted after the function is done.
        rptData = tempfile.NamedTemporaryFile()
        rCode = subprocess.call(['pdftk', pdfFile, 'dump_data', 'output', rptData.name])
        with codecs.open(rptData.name, 'rt', 'utf_8_sig') as contents :
            for line in contents :
                if line.split(':')[0] == 'NumberOfPages' :
                    return int(line.split(':')[1].strip())


    def makeFolderBackup (self, source) :
        '''Make a backup of a folder (and its subfolders).'''

        if os.path.exists(source) :
            if os.path.isdir(source) :
                target = self.incrementFileName(source + '.bak')
                shutil.copytree(source, target)
                self.terminal('Backup complete from: [' + source + '] to [' + target + '].')
                return True
            else :
                self.terminal('Warning: Source ' + source + ' is not a folder. Cannot backup folder.')
        else :
            self.terminal('FYI: Project [' + source + '] not found. Cannot backup.')


    def incrementFileName (self, fileName) :
        '''If a file of the same name already exists, increment the
        name by one by adding (1) to the end of the name before the
        extension. If an increment number already exsists, increase
        it by one (+1).'''

        def addOne (nobj) :
            n = int(nobj.group(1))
            return '(' + str(n+1) + ')'

        if os.path.exists(fileName) :
            path, fn = os.path.split(fileName)
            # Search for a previous increment number
            if re.search('\([0-9]+\)', fn) :
                fn = re.sub('\(([0-9]+)\)', addOne, fn)
            else :
                fn = re.sub('(.)\.(.)', r'\1(1).\2', fn)
            # Before returning, call itself to have the right number
            return self.incrementFileName(os.path.join(path, fn))
        else :
            return fileName


    def modeFileName (self, fileName, mode = 'draft') :
        '''Dissect a file name and turn it into a "proof" name with a timestamp.'''
        
        # FIXME: It would be nice to have an alpha character incrementer
        
        (path, fn) = os.path.split(fileName)
        fParts = fn.split('.')
        newName = mode + '_' + fParts[0] + '_' + self.ymd() + '.' + fParts[1]
        return os.path.join(path, newName)


    def makeFileHeader (self, fileName, desc = None, noEditWarn = True) :
        '''Create a header for project files which may or may not be editable.'''

    #        import pdb; pdb.set_trace()

        # Set the comment marker to '%' for .tex files
        if fileName.find('.tex') > 0 or fileName.find('.adj') > 0 or fileName.find('.piclist') > 0 :
            comMark = '%'
        else :
            comMark = '#'
        # Create a warning if needed
        if noEditWarn :
            editWarn = comMark + ' This file is auto-generated, do not bother editing it\n\n'
        else :
            editWarn = None
        # Build the output
        output = comMark + ' ' + self.fName(fileName) + ' created: ' + self.tStamp() + '\n'
        if desc :
            # Strip out extra spaces from description
            desc = re.sub('\s+', ' ', desc)
            output = output + self.commentWordWrap(comMark + ' Description: ' + desc, 70, comMark) + '\n'
        if editWarn :
            output = output + editWarn
        else :
            output = output + '\n\n'

        return output


    def dieNow (self, msg = '') :
        '''When something bad happens we don't want undue embarrasment by letting
        the system find its own place to crash.  We'll take it down with this
        command and will have hopefully provided the user with a useful message as
        to why this happened.'''

    # FIXME: Need to add a debug switch in here

        if msg :
            msg = '\n' + msg + ' Rapuma halting now!\n'
        else :
            msg = '\nRapuma halting now!\n'

        sys.exit(msg)


    def isOlder (self, first, second) :
        '''Check to see if the first file is older than the second.
        Return True if it is. This assumes that both files exist. If
        not, then throw and exception error.'''

#        import pdb; pdb.set_trace()

        try :
            return not os.path.exists(second) or (os.path.getmtime(first) < os.path.getmtime(second))
        except Exception as e :
            # If this doesn't work, we should probably quite here
            self.dieNow('Error: isOlder() failed with this error: ' + str(e))


    def isExecutable (self, fn) :
        '''Return True if the file is an executable.'''

        # Define some executable types
        executableTypes = ['py', 'sh', 'exe', 'bat', 'pl']

        # Look at file extention first
        f = self.fName(fn)
        if f.rfind('.') != -1 :
            if f[f.rfind('.')+1:] in executableTypes :
                return True
        else :
            # If no extention, look inside to find out
            # Most scripts have a she-bang in them
            fh = open(fn, 'r')
            for l in fh :
                if l[:2] == '#!' :
                    return True


    def makeExecutable (self, fileName) :
        '''Assuming fileName is a script, give the file executable permission.
        This is necessary primarily because I have not found a way to preserve
        permissions of the files comming out of a zip archive. To make sure the
        processing script will actually work when it needs to run. Changing the
        permissions to 777 may not be the best way but it will work for now. '''

        os.chmod(fileName, int("0777", 8))


    def fixExecutables (self, scriptDir) :
        '''Go through a folder and set permission on executables.'''

        try :
            for subdir, dirs, files in os.walk(scriptDir):
                for f in files:
                    if self.isExecutable(os.path.join(subdir, f)) :
                        self.makeExecutable(os.path.join(subdir, f))
        except Exception as e :
            # If this doesn't work, we should probably quite here
            self.dieNow('Error: fixExecutables() failed with this error: ' + str(e))


    def makeReadOnly (self, fileName) :
        '''Set the permissions on a file to read only.'''

        os.chmod(fileName, stat.S_IREAD)


    def makeWriteable (self, fileName) :
        '''Set the permissions on a file to writeable.'''

        os.chmod(fileName, stat.S_IWRITE)


    def utf8Copy (self, source, target) :
        '''Ensure a copy is done in utf-8 encoding.'''

        with codecs.open(source, 'rt', 'utf_8_sig') as contents :
            with codecs.open(target, 'w', 'utf_8_sig') as output :
                lines = contents.read()
                output.write(lines)


    def fName (self, fullPath) :
        '''Lazy way to extract the file name from a full path 
        using os.path.split().'''

        return os.path.split(fullPath)[1]


    def tempName (self, fileName) :
        '''Return a file name with an extra .tmp extention.'''
        
        return fileName + '.tmp'


    def resolvePath (self, path) :
        '''Resolve the '~' in a path if there is one with the actual home path.'''

        try :
            return os.path.realpath(os.path.expanduser(path))
        except :
            return None


    def macroRunner (self, macroFile) :
        '''Run a macro. This assumes the macroFile includes a full path.'''

        try :
            macro = codecs.open(macroFile, "r", encoding='utf_8')
            for line in macro :
                # Clean the line, may be a BOM to remove
                line = line.replace(u'\ufeff', '').strip()
                if line[:1] != '#' and line[:1] != '' and line[:1] != '\n' :
                    terminal('Macro line: ' + line)
                    # FIXME: Could this be done better with subprocess()?
                    os.system(line)
            return True

        except Exception as e :
            # If we don't succeed, we should probably quite here
            self.dieNow('Macro failed with the following error: ' + str(e))


    def addToList (self, thisList, item) :
        '''Generic function to add an item to any list if it isn't there already.
        If the list is empty, just do a simple append().'''

        if len(thisList) != 0 :
            if item not in thisList :
                listOrder = []
                listOrder = thisList
                listOrder.append(item)
                return listOrder
            else :
                return thisList
        else :
            thisList.append(item)
            return thisList


    def removeFromList (self, thisList, item) :
        '''Generic function to remove an item to any list if it is there.
        If not, just return the list contents or an empty list.'''

        terminal('\nError: This function is not implemented yet!\n')


    def str2bool (self, string) :
        '''Simple boolean tester'''

        if isinstance(string, basestring) and string.lower() in ['0','false','no']:
            return False
        else :
            return bool(string)


    def escapePath (self, path) :
        '''Put escape characters in a path.'''

        return path.replace("(","\\(").replace(")","\\)").replace(" ","\\ ")


    def quotePath (self, path) :
        '''Put quote markers around a path.'''

        return '\"' + path + '\"'

    def isInZip (self, fileName, fileZip) :
        '''Look for a specific file in a zip file.'''

        zipInfo = zipfile.ZipFile(fileZip)
        nList = zipInfo.namelist()
        for i in nList :
            try :
                if i.split('/')[1] == fileName :
                    return True
            except :
                return False


    def pkgExtract (self, source, targetFolder, confXml) :
        '''Extract a Rapuma package (zip file) and test for success.'''

        if zipfile.is_zipfile(source) :
            myzip = zipfile.ZipFile(source, 'r')
            myzip.extractall(targetFolder)
            # Double check extract
            if os.path.isfile(confXml) :
                return True


    def rtnUnicodeValue (self, char) :
        '''Return the Unicode value as a string.'''

        n = ord(char)
        # There are 2 ways to format the output:
        #   value = "%04X"% n
        #   value = "{:04X}".format(n)
        # The second way is prefered because it conforms to Py 3.0

        return "{:04X}".format(n)


###############################################################################
############################ Text encoding routines ###########################
###############################################################################

    def decodeText (self, fileName, sourceEncoded) :
        '''In case an encoding conversion is needed. This function will try
        to do that and if it fails, it should return a meaningful error msg.'''

        # First, test so see if we can even read the file
        try:
            fileObj = open(fileName, 'r').read()
        except Exception as e :
            terminal('decodeText() failed with the following error: ' + str(e))
            self.dieNow()
        # Now try to run the decode() function
        try:
            return fileObj.decode(sourceEncode)

        except Exception:
            terminal('decodeText() could not decode: [' + fileName + ']\n')
            self.dieNow()


###############################################################################
########################## Config/Dictionary routines #########################
###############################################################################

    def addComponentType (self, cfg, local, cType) :
        '''Add (register) a component type to the config if it 
        is not there already.'''

        Ctype = cType.capitalize()
        self.buildConfSection(cfg, 'CompTypes')
        if not cfg['CompTypes'].has_key(Ctype) :
            # Build the comp type config section
            self.buildConfSection(cfg['CompTypes'], Ctype)

            # Get persistant values from the config if there are any
            newSectionSettings = self.getPersistantSettings(cfg['CompTypes'][Ctype], os.path.join(local.rapumaConfigFolder, cType + '.xml'))
            if newSectionSettings != cfg['CompTypes'][Ctype] :
                cfg['CompTypes'][Ctype] = newSectionSettings
                # Save the setting rightaway
                self.writeConfFile(cfg)
                return cfg


    def initConfig (self, confFile, defaultFile) :
        '''Initialize or load a config file. This will load a config file if an
        existing one is there and update it with any new system default settings
        If one does not exist a new one will be created based on system default
        settings.'''

#        import pdb; pdb.set_trace()

        if not os.path.isfile(confFile) :
            configObj           = ConfigObj(self.getXMLSettings(defaultFile), encoding='utf-8')
            configObj.filename  = confFile
            self.writeConfFile(configObj)
        else :
            # But check against the default for possible new settings
            configObj           = ConfigObj(encoding='utf-8')
            orgConfigObj        = ConfigObj(confFile, encoding='utf-8')
            orgFileName         = orgConfigObj.filename
            defaultObj          = ConfigObj(self.getXMLSettings(defaultFile), encoding='utf-8')
            defaultObj.merge(orgConfigObj)
            # A key comparison should be enough to tell if it is the same or not
            if self.confObjCompare(defaultObj, orgConfigObj) :
                configObj = orgConfigObj
                configObj.filename = orgFileName
            else :
                configObj = defaultObj
                configObj.filename = orgFileName
                self.writeConfFile(configObj)

        return configObj


    def confObjCompare (self, objA, objB) :
        '''Do a simple compare on two ConfigObj objects.'''

        # Make a temp files for testing
        tmpconfA = tempfile.NamedTemporaryFile()
        tmpconfB = tempfile.NamedTemporaryFile()

        # There must be a better way to do this but this will work for now
        objA.filename = tmpconfA.name
        objA.write()
        objB.filename = tmpconfB.name
        objB.write()
        reObjA = ConfigObj(tmpconfA, encoding='utf-8')
        reObjB = ConfigObj(tmpconfB, encoding='utf-8')
        return reObjA.__eq__(reObjB)


    def getPersistantSettings (self, confSection, defaultSettingsFile) :
        '''Look up each persistant setting in a given XML config file. Check
        for the exsitance of the setting in the specified section in the users
        config file and insert the default if it does not exsit in the uers 
        config file.'''

        if os.path.isfile(defaultSettingsFile) :
            compDefaults = self.getXMLSettings(defaultSettingsFile)

            newConf = {}
            for k, v, in compDefaults.iteritems() :
                if not confSection.has_key(k) :
    # FIXME: Not sure if this next part is good or not. This will look for
    # a "None" type to be passed to it then it will replace it with an empty
    # string to outupt to the config object. This may not be the best way. 
                    if not v :
                        v = ''
                    newConf[k] = v
                else :
                    newConf[k] = confSection[k]

            return newConf


    def buildConfSection (self, confObj, section) :
        '''Build a conf object section if it doesn't exist.'''

#        import pdb; pdb.set_trace()

        if not confObj.has_key(section) :
            confObj[section] = {}
            return True


    def getXMLSettings (self, xmlFile) :
        '''Test for exsistance and then get settings from an XML file.'''

        if  os.path.exists(xmlFile) :
            return self.xml_to_section(xmlFile)
        else :
            raise IOError, "Can't open " + xmlFile


    def overrideSettings (self, settings, overrideXML) :
        '''Override the settings in an object with another like object.'''

        settings = self.xml_to_section(overrideXML)

        return settings


    def writeConfFile (self, config) :
        '''Generic routin to write out to, or create a config file.'''

#        import pdb; pdb.set_trace()

        # Build the folder path if needed
        if not os.path.exists(os.path.split(config.filename)[0]) :
            os.makedirs(os.path.split(config.filename)[0])

        # Make a backup in our temp dir case something goes dreadfully wrong
        orgConfData = tempfile.NamedTemporaryFile()
        if os.path.isfile(config.filename) :
            shutil.copy(config.filename, orgConfData.name)

        # Now do a compare on the new data set to see if there was any actual changes.
        # Writing out a "non-change" will affect other processes downstream. There may
        # be a better way to do this but this will have to do for now.
        newConfData = tempfile.NamedTemporaryFile()
        new = ConfigObj(config,  encoding='utf-8')
        new.filename = newConfData.name
        new.write()

        # Inside of diffl() open both files with universial line endings then
        # check each line for differences. This looks for an identical file
        diff = difflib.ndiff(open(newConfData.name, 'rU').readlines(), open(orgConfData.name, 'rU').readlines())
        for d in diff :
            if d[:1] == '+' or d[:1] == '-' :
                # Let's try to write it out
                try :
                    # To track when a conf file was saved as well as other general
                    # housekeeping we will create a GeneralSettings section with
                    # a last edit date key/value.
                    self.buildConfSection(config, 'GeneralSettings')
                    # If we got past that, write a time stamp
                    config['GeneralSettings']['lastEdit'] = self.tStamp()
                    # Try to write out the data now
                    config.write()
                except Exception as e :
                    terminal(u'\nERROR: Could not write to: ' + config.filename)
                    terminal(u'\nPython reported this error:\n\n\t[' + unicode(e) + ']' + unicode(config) + '\n')
                    # Recover now
                    if os.path.isfile(confData) :
                        shutil.copy(orgConfData.name, config.filename)
                    # Use raise to send out a stack trace. An error at this point
                    # is like a kernel panic. Not good at all.
                    raise
                # No need to look for more if we write out on the first findall
                break
        # Should be done if we made it this far
        return True


    def xml_to_section (self, xmlFile) :
        '''Read in our default settings from the XML system settings file'''

        # Read in our XML file
        doc = ET.parse(xmlFile)
        # Create an empty dictionary
        data = {}
        # Extract the section/key/value data
        self.xml_add_section(data, doc)
        # Convert the extracted data to a configobj and return
        return ConfigObj(data, encoding='utf-8')


    def xml_add_section (self, data, doc) :
        '''Subprocess of xml_to_section().  Adds sections in the XML to conf
        object that is in memory.  It acts only on that object and does not return
        anything.'''

#        import pdb; pdb.set_trace()

        # Find all the key and value in a setting
        sets = doc.findall('setting')
        for s in sets :
            debug_item = s.find('value')
            # This doesn't mean there is no value, rather, it means
            # the "value" marker is present in the setting data set
            if s.find('value') is not None:
                val = s.find('value').text
                # Need to treat lists special but type is not required
                if s.find('type').text == 'list' :
                    if val :
                        data[s.find('key').text] = val.split(',')
                    else :
                        data[s.find('key').text] = []
                else :
                    # We do not want "None" ending up in the config file
                    # This seems to be the best place to get rid of it.
                    if val :
                        data[s.find('key').text] = val
                    else :
                        data[s.find('key').text] = ''

        # Starting here, find all the sections then call this same function
        # to grab the keys and values all the settings in the section
        sects = doc.findall('section')
        for s in sects :
            nd = {}
            data[s.find('sectionID').text] = nd
            self.xml_add_section(nd, s)


    def override_section (self, aSection) :
        '''Overrides settings by using the XML defaults and then merging those with
        items in the configobj that match.'''

        # Look for the key and value in object of items created from itself
        for k, v in self.items() :
            if k in aSection :
                if isinstance(v, dict) and isinstance(aSection[k], dict) :
                    v.override(aSection[k])
                elif not isinstance(v, dict) and not isinstance(aSection[k], dict) :
                    self[k] = aSection[k]
        # Return the overridden object
        return self


    def xmlFileToDict (self, fileName) :
        '''This will parse an XML file and send it on to the conversion
        function to get the results.'''

        tree =  ET.parse(fileName)
        root = tree.getroot()
        return self.etree_to_dict(root)


    def etree_to_dict(self, t):
        '''Convert an XML file into a dictionary. The code for this was lifted from stackoverflow at:
        http://stackoverflow.com/questions/7684333/converting-xml-to-dictionary-using-elementtree'''

        d = {t.tag: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(self.etree_to_dict, children):
                for k, v in dc.iteritems():
                    dd[k].append(v)
            # The code in this function is generic in its original form
            # however, we needed to add a Rapuma-specific value to be able
            # to build the dictionary in a predictable way. The following
            # line was like this:
            #   d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
            # the modified line is as follows:
            d = {t.tag: {k:(v[0] if (len(v) == 1 and k != "setting") else v) for k, v in dd.iteritems()}}

        if t.attrib :
            d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())

        if t.text :
            text = t.text.strip()
            if children or t.attrib :
                if text:
                  d[t.tag]['#text'] = text
            else :
                d[t.tag] = text
        return d


    # This will reasign the standard ConfigObj function that works much like ours
    # but not quite what we need for working with XML as one of the inputs.
    Section.override = override_section


###############################################################################
################################# Terminal Output #############################
###############################################################################


    def terminal (self, msg) :
        '''Send a message to the terminal with a little formating to make it
        look nicer.'''

        # Output the message and wrap it if it is over 60 chars long.
        print self.wordWrap(msg, 60).encode(sys.getfilesystemencoding())


    def terminalError (self, msg) :
        '''Send an error message to the terminal with a little formating to make it
        look nicer.'''

        # Output the message and wrap it if it is over 60 chars long.
        print '\n' + self.wordWrap('\tError: ' + msg, 60).encode(sys.getfilesystemencoding()) + '\n'


    def wordWrap (self, text, width) :
        '''A word-wrap function that preserves existing line breaks
            and most spaces in the text. Expects that existing line
            breaks are linux style newlines (\n).'''

        def func(line, word) :
            nextword = word.split("\n", 1)[0]
            n = len(line) - line.rfind('\n') - 1 + len(nextword)
            if n >= width:
                sep = "\n"
            else:
                sep = " "
            return '%s%s%s' % (line, sep, word)
        text = text.split(" ")
        while len(text) > 1:
            text[0] = func(text.pop(0), text[0])
        return text[0]


    def commentWordWrap (self, text, width, commentMarker) :
        '''A word-wrap function that preserves existing line breaks
            and most spaces in the text. Expects that existing line
            breaks are linux style newlines (\n).'''

        def func(line, word) :
            nextword = word.split("\n", 1)[0]
            n = len(line) - line.rfind('\n') - 1 + len(nextword)
            if n >= width:
                sep = "\n" + commentMarker + '\t'
            else:
                sep = " "
            return '%s%s%s' % (line, sep, word)
        text = text.split(" ")
        while len(text) > 1:
            text[0] = func(text.pop(0), text[0])
        return text[0]


    def tStamp (self) :
        '''Create a simple time stamp for logging and timing purposes.'''

        return str(datetime.now()).split(".")[0]


    def ymd (self) :
        '''Return a year month day string (numbers).'''

        return self.tStamp().split()[0].replace('-', '')


    def time (self) :
        '''Return a simple unformated time string (h m s numbers).'''

        return self.tStamp().split()[1].replace(':', '')


    def fullFileTimeStamp (self) :
        '''Create a full time stamp that will work in a file name.'''

        return self.ymd() + self.time()


###############################################################################
########################## Misc Text File Functions ###########################
###############################################################################


