#!/usr/bin/python
# -*- coding: utf_8 -*-

# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will create an object that will hold all the general local info
# for a project.


###############################################################################
################################ Component Class ##############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import codecs, os
from configobj import ConfigObj

# Load the local classes
from rapuma.core.tools          import Tools
from rapuma.core.user_config    import UserConfig


class ProjLocal (object) :

    def __init__(self, pid) :
        '''Intitate a class object which contains all the project folder locations.'''

        self.pid                = pid
        self.rapumaHome         = os.environ.get('RAPUMA_BASE')
        self.userHome           = os.environ.get('RAPUMA_USER')
        self.user               = UserConfig()
        self.userConfig         = self.user.userConfig
        self.projHome           = self.userConfig['Projects'][pid]['projectPath']
        self.tools              = Tools()

        # Bring in all the Rapuma default project location settings
        rapumaXMLDefaults = os.path.join(self.rapumaHome, 'config', 'proj_local.xml')
        if os.path.exists(rapumaXMLDefaults) :
            lc = self.tools.xml_to_section(rapumaXMLDefaults)
        else :
            raise IOError, "Can't open " + rapumaXMLDefaults
            
        # Create a list of project folders for later processing
        self.projFolders = lc['ProjFolders'].keys()

        # Do a loopy thingy and pull out all the known settings
        localTypes = ['ProjFolders', 'UserFolders', 'RapumaFolders', 'ProjFiles', 'UserFiles', 'RapumaFiles']
        for t in localTypes :
            if t[:3].lower() == 'pro' :
                home = getattr(self, 'projHome')
            elif t[:3].lower() == 'use' :
                home = getattr(self, 'userHome')
            elif t[:3].lower() == 'rap' :
                home = getattr(self, 'rapumaHome')

            for key in lc[t] :
                # For extra credit, if we are looking at files, set the name here
                if t[-5:].lower() == 'files' :
                    if type(lc[t][key]) == list :
                        setattr(self, key + 'Name', lc[t][key][len(lc[t][key])-1])
                    else :
                        setattr(self, key + 'Name', lc[t][key])
                    # Uncomment for testing
#                    print key + 'Name = ', getattr(self, key + 'Name')

                if type(lc[t][key]) == list :
                    setattr(self, key, os.path.join(home, *lc[t][key]))
                else :
                    setattr(self, key, os.path.join(home, lc[t][key]))

                # Uncomment for testing
#                print key + ' = ', getattr(self, key)

        # Extract just the file names from these
        localTypes = ['ProjFiles', 'UserFiles', 'RapumaFiles']

        # Add some additional necessary params
        self.lockExt = '.lock'
        
        # Do some cleanup like getting rid of the last sessions error log file.
        try :
            if os.path.isfile(self.projErrorLogFile) :
                os.remove(self.projErrorLogFile)
        except :
            pass

        # Load the Rapuma conf file into an object
        self.localUserConfig = ConfigObj(self.userConfFile, encoding='utf-8')

        # Create a fresh projConfig object
        if os.path.isfile(self.projConfFile) :
            self.localProjConfig = ConfigObj(self.projConfFile, encoding='utf-8')


###############################################################################
########################### Project Local Functions ###########################
###############################################################################

#    def getGroupSourcePath (self, gid) :
#        '''Get the source path for a specified group.'''

##        import pdb; pdb.set_trace()

#        csid = self.localProjConfig['Groups'][gid]['csid']
#        try :
#            return self.localUserConfig['Projects'][self.pid][csid + '_sourcePath']
#        except Exception as e :
#            # If we don't succeed, we should probably quite here
#            terminal('Could not find the path for group: [' + gid + '], This was the error: ' + str(e))


#    def getSourceFile (self, gid, cid) :
#        '''Get the source file name with path.'''

#        from rapuma.core.paratext       import Paratext
#        sourcePath          = self.getGroupSourcePath(gid)
#        cType               = self.localProjConfig['Groups'][gid]['cType']
#        sourceEditor        = self.localProjConfig['CompTypes'][cType.capitalize()]['sourceEditor']
#        # Build the file name
#        if sourceEditor.lower() == 'paratext' :
#            sName = Paratext(self.pid).formPTName(gid, cid)
#        elif sourceEditor.lower() == 'generic' :
#            sName = Paratext(self.pid).formGenericName(gid, cid)

#        return os.path.join(sourcePath, sName)


#    def getWorkingFile (self, gid, cid) :
#        '''Return the working file name with path.'''

#        csid            = self.localProjConfig['Groups'][gid]['csid']
#        cType           = self.localProjConfig['Groups'][gid]['cType']
#        targetFolder    = os.path.join(self.projComponentsFolder, cid)
#        return os.path.join(targetFolder, cid + '_' + csid + '.' + cType)


#    def getWorkCompareFile (self, gid, cid) :
#        '''Return the working compare file (saved from last update) name with path.'''

#        return self.getWorkingFile(gid, cid) + '.cv1'


#    def getWorkingSourceFile (self, gid, cid) :
#        '''Get the working source file name with path.'''

#        targetFolder    = os.path.join(self.projComponentsFolder, cid)
#        source          = self.getSourceFile(gid, cid)
#        sName           = os.path.split(source)[1]
#        return os.path.join(targetFolder, sName + '.source')



