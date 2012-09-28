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

import codecs, os, sys, re, fileinput, zipfile
from datetime import *
from xml.etree import ElementTree
#import xml.etree.ElementTree as ElementTree

from configobj import ConfigObj, Section
import pprint

###############################################################################
############################ Functions Begin Here #############################
###############################################################################

def dieNow () :
    '''When something bad happens we don't want undue embarrasment by letting
    the system find its own place to crash.  We'll take it down with this
    command and will have hopefully provided the user with a useful message as
    to why this happened.'''

    terminal('RPM halting now!')
    sys.exit()


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


def fName (fullPath) :
    '''Lazy way to extract the file name from a full path 
    using os.path.split().'''

    return os.path.split(fullPath)[1]


def resolvePath (path) :
    '''Resolve the '~' in a path if there is one with the actual home path.'''

    if path[0] == '~' :
        try :
            # This should be the best way
            return os.path.expanduser(path)
        except :
            # Manually look for "~/" shorthand path and replace it 
            # with the actual "home"
            return path.replace('~', os.environ.get('HOME'))
    elif path == '' or path == 'None' :
        return None
    else :
        # Otherwise run abspath on it and send it on
        return os.path.abspath(path)


def addToList (thisList, item) :
    '''Generic function to add an item to any list if it isn't there already.
    If not, just return the list contents or an empty list.'''

    if len(thisList) != 0 :
        if item not in thisList :
            listOrder = []
            listOrder = thisList
            listOrder.append(item)
            return listOrder
        else :
            return thisList
    else :
        return thisList


def removeFromList (thisList, item) :
    '''Generic function to remove an item to any list if it is there.
    If not, just return the list contents or an empty list.'''

    pass


def str2bool (str) :
    '''Simple boolean tester'''

    if isinstance(str, basestring) and str.lower() in ['0','false','no']:
        return False
    else:
        return bool(str)


def escapePath (path) :
    '''Put escape characters in a path.'''

    return path.replace("(","\\(").replace(")","\\)").replace(" ","\\ ")


#def escapePath (path) :
#    '''Escape irregular characters in a path.'''

#    # FIXME: It would seem that all that is needed is to put
#    # quotes around the path to make them acceptable to
#    # system calls. For now we will use this. We might need
#    # to do more such as is commented below. Stay tuned...
#    return '"%s"' % ( path )

#    # FIXME: Be nice if we could use re instead of .replace
#    # np = re.sub(r'([ ()\"\'\[\]])', '\\1', path)


def ancestorsPath (homePath) :
    '''This will start in the current folder/directory and return the paths of
    the two directories above it.  You can't know where you are unless you know
    where you come from.'''

    parent              = os.path.dirname(homePath)
    if not os.path.isdir(parent) :
        parent = None

    grandparent         = os.path.dirname(parent)
    if not os.path.isdir(grandparent) or grandparent == parent :
        grandparent = None

    return (parent, grandparent)


def isInZip(file, zip) :
    '''Look for a specific file in a tar file.'''

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

    # To track when a conf file was saved as well as other general
    # housekeeping we will create a GeneralSettings section with
    # a last edit date key/value.
    buildConfSection(config, 'GeneralSettings')
    try :
        config['GeneralSettings']['lastEdit'] = tStamp()
        config.write()
        return True

    except :
        terminal('\nERROR: Could not write to: ' + config.filename)
        return False


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
            data[s.find('key').text] = val

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


def xmlFileToDict (fileName) :
    tree =  ElementTree.parse(fileName)
    root = tree.getroot()
    return xmlToDict(root)


def xmlToDict (element) :
    '''This will turn a normal XML file into a standard Python dictionary.
    I picked up this clever pice of code from here:
        http://stackoverflow.com/questions/2148119/how-to-convert-a-xml-string-to-a-dictionary-in-python
    A guy named josch submitted it. I have modified it a little to work in RPM.'''

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

    date_time, secs = str(datetime.now()).split(".")
    
    return date_time


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



