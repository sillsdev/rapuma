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

import codecs, os, sys
from datetime import *
from xml.etree import ElementTree
from configobj import ConfigObj, Section

# Load config specification
#configspec = ConfigObj(configspecfilename, encoding='UTF8',
#                       list_values=False, _inspec=True)
#config = ConfigObj(filename, configspec=configspec)

###############################################################################
############################ Functions Begin Here #############################
###############################################################################

def str2bool(str):
    '''Simple boolean tester'''

    if isinstance(str, basestring) and str.lower() in ['0','false','no']:
        return False
    else:
        return bool(str)


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


def isRecordedProject (userConfig, pid) :
    '''Check to see if this project is recorded in the user's config'''

    try :
        return pid in userConfig['Projects']
    except :
        pass


def recordProject (userConfig, projConfig, projHome) :
    '''Add information about this project to the user's rpm.conf located in
    the home config folder.'''

    pid     = projConfig['ProjectInfo']['projectIDCode']
    pname   = projConfig['ProjectInfo']['projectName']
    ptype   = projConfig['ProjectInfo']['projectType']
    date    = projConfig['ProjectInfo']['projectCreateDate']
    if not isRecordedProject(userConfig, pid) :

        # FIXME: Before we create a project entry we want to be sure that
        # the projects section already exsists.  There might be a better way
        # of doing this.
        try :
            userConfig['Projects'][pid] = {}
        except :
            userConfig['Projects'] = {}
            userConfig['Projects'][pid] = {}

        # Now add the project data
        userConfig['Projects'][pid]['projectName']          = pname
        userConfig['Projects'][pid]['projectType']          = ptype
        userConfig['Projects'][pid]['projectPath']          = projHome
        userConfig['Projects'][pid]['projectCreateDate']    = date
        userConfig.write()
        return True
    else :
        return False


def mergeConfig (orgConfig, rpmConfigFile) :
    '''Generic function to return a merged config object
    from a valid XML config file. The orgConfig is ConfigObj
    object and rpmConfigFile is a valid RPM XML config file.'''

    xmlConfig = getXMLSettings(rpmConfigFile)
    # Create a new conf object based on all the XML default settings
    # Then override them with any exsiting project settings.
    newConfig = ConfigObj(xmlConfig.dict()).override(orgConfig)
    for s,v in orgConfig.items() :
        if s not in newConfig :
            newConfig[s] = v

    return newConfig


#def getXMLOverrideSettings (rpm, user) :
#    '''Get the XML settings then override them if needed.'''

#    res = getXMLSettings(rpm)
#    if os.path.isfile(user) :
#        return overrideSettings(res, user)
#    else :
#        return res


#def getCompInitSettings (userHome, rpmHome, compType) :
#    '''Get the project initialisation settings from the project type init xml
#    file.  Then, if it exsits, override these settings with the version found in
#    the user area.'''

#    rpmCompInitXML     = os.path.join(rpmHome, 'resources', 'lib_compTypes', compType, compType + '_init.xml')
#    userCompInitXML     = os.path.join(userHome, 'resources', 'lib_compTypes', compType, compType + '_init.xml')
#    return getXMLOverrideSettings(rpmCompInitXML, userCompInitXML)


#def getCompSettings (userHome, rpmHome, compType) :
#    '''Get the default settings out of a component type xml description file.'''

#    rpmCompXML     = os.path.join(rpmHome, 'resources', 'lib_compTypes', compType, compType + '.xml')
#    userCompXML     = os.path.join(userHome, 'resources', 'lib_compTypes', compType, compType + '.xml')

#    res = getXMLSettings(rpmCompXML)
#    if os.path.isfile(userCompXML) :
#        return overrideSettings(res, userCompXML)
#    else :
#        return res


def getXMLSettings (xmlFile) :
    '''Get settings from an XML file.'''

    if  os.path.exists(xmlFile) :
        return xml_to_section(xmlFile)
    else :
        raise IOError, "Can't open " + xmlFile


def overrideSettings (settings, overrideXML) :
    '''Override the settings in an object with another like object.'''

    settings = xml_to_section(overrideXML)

    return settings


def writeConfFile (configStuff, configFileAndPath) :
    '''Generic routin to write out to, or create a config file.'''

    # Parse file and path
    (folderPath, configFile) = os.path.split(configFileAndPath)

    # Build the folder path if needed
    if not os.path.exists(folderPath) :
        os.makedirs(folderPath)

    # Create the file if needed
    if not os.path.isfile(configFileAndPath) or os.path.getsize(configFileAndPath) == 0 :
        writeObject = codecs.open(configFileAndPath, "w", encoding='utf_8')
        writeObject.close()

    # To track when a conf file was saved as well as other general
    # housekeeping we will create a GeneralSettings section with
    # a last edit date key/value.
    buildConfSection(configStuff, 'GeneralSettings')
    try :
        configStuff['GeneralSettings']['lastEdit'] = tStamp()
        configStuff.filename = configFileAndPath
        configStuff.write()
        return True

    except :
        terminal('\nERROR: Could not write to: ' + fileName)
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


# This will reasign the standard ConfigObj function that works much like ours
# but not quite what we need for working with XML as one of the inputs.
Section.override = override_section


############################### Terminal Output ###############################

def terminal (msg) :
    '''Send a message to the terminal with a little formating to make it
    look nicer.'''

    # Output the message and wrap it if it is over 60 chars long.
    print wordWrap(msg, 60)


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



