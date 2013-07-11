#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os, shutil
from configobj                          import ConfigObj

# Load the local classes
from rapuma.core.tools                  import Tools, ToolsPath, ToolsGroup
from rapuma.core.user_config            import UserConfig
from rapuma.core.proj_local             import ProjLocal
from rapuma.core.proj_log               import ProjLog

###############################################################################
################################## Begin Class ################################
###############################################################################

class ProjConfig (object) :

    def __init__(self, pid, gid = None) :
        '''Do the primary initialization for this class.'''

        self.pid                            = pid
        self.gid                            = gid
        self.user                           = UserConfig()
        self.userConfig                     = self.user.userConfig
        self.projHome                       = self.userConfig['Projects'][self.pid]['projectPath']
        self.mType                          = self.userConfig['Projects'][self.pid]['projectMediaIDCode']
        self.local                          = ProjLocal(self.pid)
        self.tools                          = Tools()
        self.log                            = ProjLog(self.pid)
        # File names
        self.projConfFileName               = 'project.conf'
        self.progConfXmlFileName            = self.mType + '.xml'
        self.layoutConfFileName             = 'layout.conf'
        self.layoutXmlConfFileName          = self.mType + '_layout.xml'







# FIXME: in a TeX world view, the fonts are tied to the macPack. The font config
# info will the macPack and the font conf will go away. The information in the
# font xml will be merged in

        self.fontConfFileName               = 'font.conf'
        self.fontXmlConfFileName            = 'font.xml'







        self.adjustmentConfFileName         = 'adjustment.conf'
        self.adjustmentXmlConfFileName      = 'adjustment.xml'
        self.hyphenConfFileName             = 'hyphenation.conf'
        self.hyphenXmlConfFileName          = 'hyphenation.xml'
        self.illustrationConfFileName       = 'illustration.conf'
        self.illustrationXmlConfFileName    = 'illustration.xml'
        # Paths
        self.projConfFolder                 = self.local.projConfFolder
        self.rapumaConfigFolder             = self.local.rapumaConfigFolder
        # Files with paths
        self.projConfFile                   = os.path.join(self.projConfFolder, self.projConfFileName)
        self.projConfXmlFile                = os.path.join(self.rapumaConfigFolder, self.progConfXmlFileName)
        self.layoutConfFile                 = os.path.join(self.projConfFolder, self.layoutConfFileName)
        self.layoutXmlConfFile              = os.path.join(self.rapumaConfigFolder, self.layoutXmlConfFileName)
        self.fontConfFile                   = os.path.join(self.projConfFolder, self.fontConfFileName)
        self.fontXmlConfFile                = os.path.join(self.rapumaConfigFolder, self.fontXmlConfFileName)
        self.adjustmentConfFile             = os.path.join(self.projConfFolder, self.adjustmentConfFileName)
        self.adjustmentXmlConfFile          = os.path.join(self.rapumaConfigFolder, self.adjustmentXmlConfFileName)
        self.hyphenConfFile                 = os.path.join(self.projConfFolder, self.hyphenConfFileName)
        self.hyphenXmlConfFile              = os.path.join(self.rapumaConfigFolder, self.hyphenXmlConfFileName)
        self.illustrationConfFile           = os.path.join(self.projConfFolder, self.illustrationConfFileName)
        self.illustrationXmlConfFile        = os.path.join(self.rapumaConfigFolder, self.illustrationXmlConfFileName)
        # Load the config objects
        self.adjustmentConfig               = self.tools.initConfig(self.adjustmentConfFile, self.adjustmentXmlConfFile)
        self.layoutConfig                   = self.tools.initConfig(self.layoutConfFile, self.layoutXmlConfFile)
        self.fontConfig                     = self.tools.initConfig(self.fontConfFile, self.fontXmlConfFile)
        self.projConfig                     = self.tools.initConfig(self.local.projConfFile, self.projConfXmlFile)
        self.hyphenConfig                   = self.tools.initConfig(self.hyphenConfFile, self.hyphenXmlConfFile)
        self.illustrationConfig             = self.tools.initConfig(self.illustrationConfFile, self.illustrationXmlConfFile)

        self.tools_path                     = ToolsPath(self.local, self.projConfig, self.userConfig)
        self.tools_group                    = ToolsGroup(self.local, self.projConfig, self.userConfig)

        # For a cleaner init we will test for gid
        if gid :
            self.finishInit()
        else :
            self.cType                      = ''
            self.Ctype                      = ''
            self.macPack                    = ''

        # Log messages for this module
        self.errorCodes     = {
            'LYOT-000' : ['MSG', 'Layout module messages'],
            'LYOT-010' : ['LOG', 'Wrote out new layout configuration file. (layout.__init__())'],
            'LYOT-020' : ['LOG', 'Loaded exsisting layout configuration file. (layout.__init__())'],
            'LYOT-030' : ['LOG', 'Changes found in the default layout config model. These were merged into the exsisting layout configuration file. (layout.__init__())'],

            '0000' : ['MSG', 'Placeholder message'],

        }


    def finishInit (self) :
        '''Finishing collecting settings that would be needed for most
        functions in this module.'''

#        import pdb; pdb.set_trace()

        self.cType                          = self.projConfig['Groups'][self.gid]['cType']
        self.Ctype                          = self.cType.capitalize()
        self.macPack                        = self.projConfig['CompTypes'][self.Ctype]['macroPackage']
        # File Names
        self.macPackXmlConfFileName         = self.macPack + '.xml'
        self.macPackConfFileName            = self.macPack + '.conf'
        self.macPackFileName                = self.macPack + '.zip'
        # Folder paths
        self.projMacrosFolder               = self.local.projMacrosFolder
        self.projMacPackFolder              = os.path.join(self.local.projMacrosFolder, self.macPack)
        self.rapumaMacrosFolder             = self.local.rapumaMacrosFolder
        # File names with paths
        self.macPackConfFile                = os.path.join(self.projConfFolder, self.macPackConfFileName)
        self.macPackXmlConfFile             = os.path.join(self.projMacrosFolder, self.macPack, self.macPackXmlConfFileName)
        self.rapumaMacPackFile              = os.path.join(self.rapumaMacrosFolder, self.macPackFileName)
        # Load the macro package config
        if not os.path.exists(self.macPackXmlConfFile) :
            self.tools.pkgExtract(self.rapumaMacPackFile, self.projMacrosFolder, self.macPackXmlConfFile)

        self.macPackConfig                  = self.tools.initConfig(self.macPackConfFile, self.macPackXmlConfFile)


###############################################################################
############################ Manager Level Functions ##########################
###############################################################################
####################### Error Code Block Series = 1000 ########################
###############################################################################


    def makeNewProjConf (self, local, pid, pmid, pname, cVersion) :
        '''Create a new project configuration file for a new project.'''

        self.projConfig = ConfigObj(self.tools.getXMLSettings(os.path.join(local.rapumaConfigFolder, pmid + '.xml')), encoding='utf-8')
        # Insert intitial project settings
        self.projConfig['ProjectInfo']['projectMediaIDCode']        = pmid
        self.projConfig['ProjectInfo']['projectName']               = pname
        self.projConfig['ProjectInfo']['projectCreatorVersion']     = cVersion
        self.projConfig['ProjectInfo']['projectCreateDate']         = self.tools.tStamp()
        self.projConfig['ProjectInfo']['projectIDCode']             = pid
        self.projConfig.filename                                    = local.projConfFile
        self.projConfig.write()


###############################################################################
###############################################################################
############################ Config Handling Class ############################
###############################################################################
###############################################################################

class ConfigTools (object) :
    '''Configuration handling functions.'''

    def __init__(self, pid, gid) :

        self.pid                            = pid
        self.gid                            = gid
        self.proj_config                    = ProjConfig(pid, gid)
        self.projConfig                     = self.proj_config.projConfig
        self.layoutConfig                   = self.proj_config.layoutConfig
        self.macPackConfig                  = self.proj_config.macPackConfig
        self.csid                           = self.projConfig['Groups'][gid]['csid']
        self.cType                          = self.projConfig['Groups'][gid]['cType']
        self.Ctype                          = self.cType.capitalize()
        self.local                          = ProjLocal(pid)
        self.tools                          = Tools()
        self.log                            = ProjLog(pid)
        self.macPack                        = self.projConfig['CompTypes'][self.Ctype]['macroPackage']
        # Paths we may need
        self.projMacrosFolder               = self.local.projMacrosFolder
        self.projMacPackFolder              = os.path.join(self.projMacrosFolder, self.macPack)
        self.projComponentsFolder           = self.local.projComponentsFolder

        self.errorCodes     = {

            '0000' : ['MSG', 'Placeholder message'],

        }


###############################################################################
######################## Basic Config Handling Functions ######################
###############################################################################
####################### Error Code Block Series = 1000 ########################
###############################################################################


    def processSinglePlaceholder (self, ph, value) :
        '''Once we are sure we have a single placeholder (noting embedded) this
        will process it and replace it with the correct value.'''

        holderType = ph.split(':')[0]
        try :
            holderKey = ph.split(':')[1]
        except :
            holderKey = ''

        if self.hasPlaceHolder(value):
            value = self.processNestedPlaceholders(value, '')

        result = ph # If nothing matches below, default to returning placeholder unchanged
        if holderType == 'v' :
            result = value
        # A value that needs a measurement unit attached
        elif holderType == 'vm' :
            result = self.addMeasureUnit(value)
        # A value that is from a configObj
        elif holderKey and holderType == 'config' :
            result = self.getConfigValue(holderKey)
        # A value that is a path
        elif holderKey and holderType == 'path' :
            result = getattr(self.local, holderKey)
        # A value that is from a configObj
        elif holderKey and holderType == 'function' :
            fnc = getattr(self, holderKey)
            result = fnc()
        # A value that is a path separater character
        elif holderType == 'pathSep' :
            result = os.sep
        # A value that contains a system delclaired value
        # Note this only works if the value we are looking for has
        # been declaired above in the module init
        elif holderType == 'self' :
            result = getattr(self, holderKey)

        return result


    def processNestedPlaceholders (self, line, value = '') :
        '''Search a string (or line) for a type of Rapuma placeholder and
        insert the value. This is for building certain kinds of config values.'''

#        print "Debug: line =", line
#        print "value =", value
        result = []
        #resultline = line
        end_of_previous_segment = 0
        for (ph_start, ph_end) in self.getPlaceHolder(line) :
            unchanged_segment = line[end_of_previous_segment:ph_start]
            result.append(unchanged_segment)
            ph_text = line[ph_start+1:ph_end]
            replacement = self.processNestedPlaceholders(ph_text, value)
            result.append(unicode(replacement))
            end_of_previous_segment = ph_end+1  # Skip the closing bracket
        result.append(line[end_of_previous_segment:])
        resultline = "".join(result)
        result_text = self.processSinglePlaceholder(resultline, value)
#        print "result of processNestedPlaceholders =", result_text
        return result_text


    def hasPlaceHolder (self, line) :
        '''Return True if this line has a data place holder in it.'''

        # If things get more complicated we may need to beef this up a bit
        if line.find('[') > -1 and line.find(']') > -1 :
            return True


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


    def getConfigValue (self, val) :
        '''Return the value from a config function or just pass the
        value through, unchanged.'''

        val = val.split('|')
        dct = ['self.' + val[0]]
        val.remove(val[0])
        for i in val :
            dct.append('["' + i + '"]')

        return eval(''.join(dct))


    def addMeasureUnit (self, val) :
        '''Return the value with the specified measurement unit attached.'''
        
        mu = self.layoutConfig['GeneralSettings']['measurementUnit']
        return val + mu


###############################################################################
######################## Dynamic Config Value Functions #######################
###############################################################################
####################### Error Code Block Series = 3000 ########################
###############################################################################

    def getTopMarginFactor (self) :
        '''Calculate the top margin factor based on what the base margin
        and top margin settings are.'''

        marginUnit = float(self.layoutConfig['PageLayout']['marginUnit'])
        topMargin = float(self.layoutConfig['PageLayout']['topMargin'])
        return topMargin / marginUnit


    def getBottomMarginFactor (self) :
        '''Calculate the bottom margin factor based on what the base margin
        and bottom margin settings are.'''

        marginUnit = float(self.layoutConfig['PageLayout']['marginUnit'])
        bottomMargin = float(self.layoutConfig['PageLayout']['bottomMargin'])
        return bottomMargin / marginUnit


    def getSideMarginFactor (self) :
        '''Calculate the side margin factor based on what the base margin
        and outside margin settings are.'''

        # For this we will be using the outsideMargin setting not the inside
        marginUnit = float(self.layoutConfig['PageLayout']['marginUnit'])
        outsideMargin = float(self.layoutConfig['PageLayout']['outsideMargin'])
        insideMargin = float(self.layoutConfig['PageLayout']['insideMargin'])
        # Check the inside margin for changes (counts on the inside always > outside)
        if self.getBindingGutterWidth() > 0 :
            self.layoutConfig['PageLayout']['useBindingGutter'] = True
        else :
            self.layoutConfig['PageLayout']['useBindingGutter'] = False

        self.tools.writeConfFile(self.layoutConfig)

        return outsideMargin / marginUnit


    def getBindingGutterWidth (self) :
        '''Calculate the binding gutter width based on any extra space added
        to the inside margin which exceeds the outside margin.'''

        insideMargin = float(self.layoutConfig['PageLayout']['insideMargin'])
        outsideMargin = float(self.layoutConfig['PageLayout']['outsideMargin'])
        return insideMargin - outsideMargin





