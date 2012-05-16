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

import codecs, os, sys, re, fileinput
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


def str2bool (str) :
    '''Simple boolean tester'''

    if isinstance(str, basestring) and str.lower() in ['0','false','no']:
        return False
    else:
        return bool(str)


def escapePath (path) :
    '''Escape irregular characters in a path.'''

    # FIXME: It would seem that all that is needed is to put
    # quotes around the path to make them acceptable to
    # system calls. For now we will use this. We might need
    # to do more such as is commented below. Stay tuned...
    return '"%s"' % ( path )

#    return '"%s"' % (
#        path
#        .replace('\\', '\\\\')
#        .replace('"', '\"')
#        .replace('$', '\$')
#        .replace('`', '\`')
#        .replace(' ', '\ ')
#    )

    # FIXME: Be nice if we could use re instead of .replace
    # np = re.sub(r'([ ()\"\'\[\]])', '\\1', path)



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

    print 'Fix isinstance() problem in tools.xmlToDict()'
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
################################# Logging routines ############################
###############################################################################

# These have to do with keeping a running project log file.  Everything done is
# recorded in the log file and that file is trimmed to a length that is
# specified in the system settings.  Everything is channeled to the log file but
# depending on what has happened, they are classed in three levels:
#   1) Common event going to log and terminal
#   2) Warning event going to log and terminal if debugging is turned on
#   3) Error event going to the log and terminal

def writeToLog (project, code, msg, mod = None) :
    '''Send an event to the log file. and the terminal if specified.
    Everything gets written to the log.  Whether a message gets written to
    the terminal or not depends on what type (code) it is.  There are four
    codes:
        MSG = General messages go to both the terminal and log file
        LOG = Messages that go only to the log file
        WRN = Warnings that go to the terminal and log file
        ERR = Errors that go to both the terminal and log file.'''

    # Get information from the project object
    local = project.local
    uc = project.userConfig

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
    if os.path.isfile(local.projConfFile) :

        # Build the event line
        if code == 'ERR' :
            eventLine = '\"' + tStamp() + '\", \"' + code + '\", \"' + mod + msg + '\"'
        else :
            eventLine = '\"' + tStamp() + '\", \"' + code + '\", \"' + msg + '\"'

        # Do we need a log file made?
        try :
            if not os.path.isfile(local.projLogFile) or os.path.getsize(local.projLogFile) == 0 :
                writeObject = codecs.open(local.projLogFile, "w", encoding='utf_8')
                writeObject.write('RPM event log file created: ' + tStamp() + '\n')
                writeObject.close()

            # Now log the event to the top of the log file using preAppend().
            preAppend(eventLine, local.projLogFile)

            # Write errors and warnings to the error log file
            if code == 'WRN' and uc['System']['debugging'] == 'True':
                writeToErrorLog(local.projErrorLogFile, eventLine)

            if code == 'ERR' :
                writeToErrorLog(local.projErrorLogFile, eventLine)

        except :
            terminal("Failed to write message to log file: " + msg)

    return


def writeToErrorLog (errorLog, eventLine) :
    '''In a perfect world there would be no errors, but alas there are and
    we need to put them in a special file that can be accessed after the
    process is run.  The error file from the previous session is deleted at
    the begining of each new run.'''

    try :
        # Because we want to read errors from top to bottom, we don't pre append
        # them to the error log file.
        if not os.path.isfile(errorLog) :
            writeObject = codecs.open(errorLog, "w", encoding='utf_8')
        else :
            writeObject = codecs.open(errorLog, "a", encoding='utf_8')

        # Write and close
        writeObject.write(eventLine + '\n')
        writeObject.close()
    except :
        terminal('Error writing this event to error log: ' + eventLine)

    return


def preAppend (line, file_name) :
    '''Got the following code out of a Python forum.  This will pre-append a
    line to the begining of a file.'''

    fobj = fileinput.FileInput(file_name, inplace=1)
    first_line = fobj.readline()
    sys.stdout.write("%s\n%s" % (line, first_line))
    for line in fobj:
        sys.stdout.write("%s" % line)

    fobj.close()


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


############################### Terminal Output ###############################

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



