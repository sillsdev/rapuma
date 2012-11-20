#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20110823
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This module will hold all the miscellaneous functions that are shared with
# many other scripts in the system.

# History:
# 20111202 - djd - Start over with manager-centric model


###############################################################################
################################## Tools Class ################################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os, sys, re, fileinput, zipfile, shutil
from datetime import *
from xml.etree import ElementTree
#import xml.etree.ElementTree as ElementTree

from configobj import ConfigObj, Section

###############################################################################
############################ Functions Begin Here #############################
###############################################################################

def dieNow (msg = '') :
    '''When something bad happens we don't want undue embarrasment by letting
    the system find its own place to crash.  We'll take it down with this
    command and will have hopefully provided the user with a useful message as
    to why this happened.'''

    if msg :
        '\n' + msg + ' Rapuma halting now!\n'
    else :
        msg = '\nRapuma halting now!\n'

    sys.exit(msg)


def isOlder (child, parent) :
    '''Check to see if the child (dependent) is older (has accumulated more
    time) than the parent.  Return true if it is.'''

    # If the child file is missing, it cannot be older than the parent
    if not os.path.isfile(child) :
        return False

    childTime = int(os.path.getctime(child))
    parentTime = int(os.path.getctime(parent))
    if childTime < parentTime :
        return True
    else :
        return False


def isExecutable (fn) :
    '''Use the file exention to determine if a file is an executable script 
    or not. This may need to be expanded as use cases arrise. Simple is
    good for now. This will test for exsistance and extention type.'''

    try :
        if os.path.isfile(fn) :
            if fName(fn).split('.')[1] in ['sh', 'py', 'rapumaDemo'] :
                return True
    except Exception as e :
        # If we don't succeed, we should probably quite here
        dieNow('Little problem with tools.isExecutable(): ' + str(e) + '  File: ' + fn)


def makeExecutable (fileName) :
    '''Assuming fileName is a script, give the file executable permission.
    This is necessary primarily because I have not found a way to preserve
    permissions of the files comming out of a zip archive. To make sure the
    processing script will actually work when it needs to run. Changing the
    permissions to 777 may not be the best way but it will work for now. '''

    os.chmod(fileName, int("0777", 8))


def fName (fullPath) :
    '''Lazy way to extract the file name from a full path 
    using os.path.split().'''

    return os.path.split(fullPath)[1]


def resolvePath (path) :
    '''Resolve the '~' in a path if there is one with the actual home path.'''

    try :
        return os.path.realpath(os.path.expanduser(path))
    except :
        return None

# FIXME: This code is depricated but we may need to deal with '~'
#    if path[0] == '~' :
#        try :
#            # This should be the best way
#            return os.path.expanduser(path)
#        except :
#            # Manually look for "~/" shorthand path and replace it 
#            # with the actual "home"
#            return path.replace('~', os.environ.get('HOME'))
#    elif path == '' or path == 'None' :
#        return None
#    else :
#        # Otherwise run abspath on it and send it on
#        return os.path.abspath(path)


def addToList (thisList, item) :
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


def removeFromList (thisList, item) :
    '''Generic function to remove an item to any list if it is there.
    If not, just return the list contents or an empty list.'''

    pass


def str2bool (str) :
    '''Simple boolean tester'''

    if isinstance(str, basestring) and str.lower() in ['0','false','no']:
        return False
    else :
        return bool(str)


def escapePath (path) :
    '''Put escape characters in a path.'''

    return path.replace("(","\\(").replace(")","\\)").replace(" ","\\ ")


def quotePath (path) :
    '''Put quote markers around a path.'''

    return '\"' + path + '\"'

def isInZip(file, zip) :
    '''Look for a specific file in a zip file.'''

    zipInfo = zipfile.ZipFile(zip)
    nList = zipInfo.namelist()
    for i in nList :
        try :
            if i.split('/')[1] == file :
                return True
        except :
            return False


###############################################################################
########################## Config/Dictionary routines #########################
###############################################################################


def confObjCompare (objA, objB, path) :
    '''Do a simple compare on two ConfigObj objects.'''

    # There must be a better way to do this but this will work for now
    objA.filename = os.path.join(path, '.confA')
    objA.write()
    objB.filename = os.path.join(path, '.confB')
    objB.write()
    reObjA = ConfigObj(os.path.join(path, '.confA'))
    reObjB = ConfigObj(os.path.join(path, '.confB'))
    return reObjA.__eq__(reObjB)


def getPersistantSettings (confSection, defaultSettingsFile) :
    '''Look up each persistant setting in a given XML config file. Check
    for the exsitance of the setting in the specified section in the users
    config file and insert the default if it does not exsit in the uers 
    config file.'''

    if os.path.isfile(defaultSettingsFile) :
        compDefaults = getXMLSettings(defaultSettingsFile)

        newConf = {}
        for k, v, in compDefaults.iteritems() :
            if not testForSetting(confSection, k) :
# FIXME: Not sure if this next part is good or not. This will look for
# a "None" type to be passed to it then it will replace it with an empty
# string to outupt to the config object. This may not be the best way. 
#                if not v :
#                    v = ''
                newConf[k] = v
            else :
                newConf[k] = confSection[k]

        return newConf


def testForSetting (conf, key1, key2 = None) :
    '''Using a try statement, this will test for a setting in a config object.
    If its not there it returns None.'''

    try :
        if key2 :
            return conf[key1][key2]
        else :
            return conf[key1]
    except :
        return


def isConfSection (confObj, section) :
    '''A simple test to see if a section in a conf object is valid'''

    try :
        s = confObj[section]
        return True
    except :
        return False


def buildConfSection (confObj, section) :
    '''Build a conf object section if it doesn't exist.'''

    if not isConfSection (confObj, section) :
        confObj[section] = {}
        return True


def getXMLSettings (xmlFile) :
    '''Test for exsistance and then get settings from an XML file.'''

    if  os.path.exists(xmlFile) :
        return xml_to_section(xmlFile)
    else :
        raise IOError, "Can't open " + xmlFile


def overrideSettings (settings, overrideXML) :
    '''Override the settings in an object with another like object.'''

    settings = xml_to_section(overrideXML)

    return settings


def writeConfFile (config) :
    '''Generic routin to write out to, or create a config file.'''

    # Build the folder path if needed
    if not os.path.exists(os.path.split(config.filename)[0]) :
        os.makedirs(os.path.split(config.filename)[0])
        
    # Make a backup in case something goes dreadfully wrong
    if os.path.isfile(config.filename) :
        shutil.copy(config.filename, config.filename + '~')

    # Let's try to write it out
    try :
        # Try to write first
        config.write()

    except Exception as e :
        terminal('\nERROR: Could not write to: ' + config.filename)
        terminal('\nPython reported this error:\n\n\t[' + str(e) + ']\n')
        # Recover now
        if os.path.isfile(config.filename + '~') :
            shutil.copy(config.filename + '~', config.filename)
        # We did all we could, quite while we are ahead
        dieNow()

    # To track when a conf file was saved as well as other general
    # housekeeping we will create a GeneralSettings section with
    # a last edit date key/value.
    buildConfSection(config, 'GeneralSettings')
    # If we got past that, write a time stamp
    config['GeneralSettings']['lastEdit'] = tStamp()
    config.write()

    # Should be done if we made it this far
    return True


def xml_to_section (fname) :
    '''Read in our default settings from the XML system settings file'''

    # Read in our XML file
    doc = ElementTree.parse(fname)
    # Create an empty dictionary
    data = {}
    # Extract the section/key/value data
    xml_add_section(data, doc)
    # Convert the extracted data to a configobj and return
    return ConfigObj(data)


def xml_add_section (data, doc) :
    '''Subprocess of xml_to_section().  Adds sections in the XML to conf
    object that is in memory.  It acts only on that object and does not return
    anything.'''

    # Find all the key and value in a setting
    sets = doc.findall('setting')
    for s in sets :
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

    # Find all the sections then call this same function to grab the keys and
    # values all the settings in the section
    sects = doc.findall('section')
    for s in sects :
        nd = {}
        data[s.find('sectionID').text] = nd
        xml_add_section(nd, s)


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


#def override_section (self, aSection) :
#    '''Overrides settings by using the XML defaults and then merging those with
#    items in the configobj that match.'''

#    # Look for the key and value in object of items created from itself
#    for k, v in self.items() :
#        if k in aSection :
#            if isinstance(v, dict) and isinstance(aSection[k], dict) :
#                v.override(aSection[k])
#            elif not isinstance(v, dict) and not isinstance(aSection[k], dict) :
#                self[k] = aSection[k]
#    # Return the overridden object
#    return self


def xmlFileToDict (fileName) :
    tree =  ElementTree.parse(fileName)
    root = tree.getroot()
    return xmlToDict(root)


def xmlToDict (element) :
    '''This will turn a normal XML file into a standard Python dictionary.
    I picked up this clever pice of code from here:
        http://stackoverflow.com/questions/2148119/how-to-convert-a-xml-string-to-a-dictionary-in-python
    A guy named josch submitted it. I have modified it a little to work in Rapuma.'''

    # FIXME: print 'Fix isinstance() problem in tools.xmlToDict()'
#    if not isinstance(element, ElementTree.Element):
#        raise ValueError("must pass xml.etree.ElementTree.Element object")

    def xmltodict_handler(parent_element):
        result = dict()
        for element in parent_element:
            if len(element):
                obj = xmltodict_handler(element)
            else:
                obj = element.text

            if result.get(element.tag):
                if hasattr(result[element.tag], "append"):
                    result[element.tag].append(obj)
                else:
                    result[element.tag] = [result[element.tag], obj]
            else:
                result[element.tag] = obj
        return result

    # Return the dictionary
    return {element.tag: xmltodict_handler(element)}


# This will reasign the standard ConfigObj function that works much like ours
# but not quite what we need for working with XML as one of the inputs.
Section.override = override_section


###############################################################################
################################# Terminal Output #############################
###############################################################################


def terminal (msg) :
    '''Send a message to the terminal with a little formating to make it
    look nicer.'''

    # Output the message and wrap it if it is over 60 chars long.
    print wordWrap(msg, 60)


def terminalError (msg) :
    '''Send an error message to the terminal with a little formating to make it
    look nicer.'''

    # Output the message and wrap it if it is over 60 chars long.
    print '\n' + wordWrap('\tError: ' + msg, 60) + '\n'


def wordWrap (text, width) :
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


def tStamp () :
    '''Create a simple time stamp for logging and timing purposes.'''

    return str(datetime.now()).split(".")[0]


def ymd () :
    '''Return a year month day string (numbers).'''

    return tStamp().split()[0].replace('-', '')


def time () :
    '''Return a simple unformated time string (h m s numbers).'''

    return tStamp().split()[1].replace(':', '')


def fullFileTimeStamp () :
    '''Create a full time stamp that will work in a file name.'''

    return ymd() + time()


###############################################################################
########################## Misc Text File Functions ###########################
###############################################################################

def trimLog (logFile, limit = 1000) :
    '''Trim a log file.  This will take an existing log file and
    trim it to the amount specified in the system file.'''

    # Of course this isn't needed if there isn't even a log file
    if os.path.isfile(logFile) :

        # Change this to an int()
        limit = int(limit)
        
        # Read in the existing log file
        readObject = codecs.open(logFile, "r", encoding='utf_8')
        lines = readObject.readlines()
        readObject.close()

        # Process only if we have enough lines
        if len(lines) > limit :
            writeObject = codecs.open(logFile, "w", encoding='utf_8')
            lineCount = 0
            for line in lines :
                if limit > lineCount :
                    writeObject.write(line)
                    lineCount +=1

            writeObject.close()

        return True
    else :
        return False


