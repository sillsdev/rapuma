#!/usr/bin/python
# -*- coding: utf_8 -*-
# version: 20111207
# By Dennis Drescher (dennis_drescher at sil.org)

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This class will handle book project tasks.

# History:
# 20111222 - djd - Started with intial file


###############################################################################
################################# Project Class ###############################
###############################################################################
# Firstly, import all the standard Python modules we need for
# this process

import os
from pprint import pprint


# Load the local classes
from tools import *
from component import Component


###############################################################################
################################## Begin Class ################################
###############################################################################

# As we load the module we will bring in all the common information about all the
# components this type will handle.

# All valid USFM IDs
compIDs = {
            'gen' : ['Genesis', '01'], 'exo' : ['Exodus', '02'], 'lev' : ['Leviticus', '03'], 'num' : ['Numbers', '04'], 
            'deu' : ['Deuteronomy', '05'], 'jos' : ['Joshua', '06'], 'jdg' : ['Judges', '07'], 'rut' : ['Ruth', '08'], 
            '1sa' : ['1 Samuel', '09'], '2sa' : ['2 Samuel', '10'], '1ki' : ['1 Kings', '11'], '2ki' : ['2 Kings', '12'], 
            '1ch' : ['1 Chronicles', '13'], '2ch' : ['2 Chronicles', '14'], 'ezr' : ['Ezra', '15'], 'neh' : ['Nehemiah', '16'], 
            'est' : ['Esther', '17'], 'job' : ['Job', '18'], 'psa' : ['Psalms', '19'], 'pro' : ['Proverbs', '20'], 'ecc' : ['Ecclesiastes', '21'], 
            'sng' : ['Song of Songs', '22'], 'isa' : ['Isaiah', '23'], 'jer' : ['Jeremiah', '24'], 'lam' : ['Lamentations', '25'], 
            'ezk' : ['Ezekiel', '26'], 'dan' : ['Daniel', '27'], 'hos' : ['Hosea', '28'], 'jol' : ['Joel', '29'], 
            'amo' : ['Amos', '30'], 'oba' : ['Obadiah', '31'], 'jon' : ['Jonah', '32'], 'mic' : ['Micah', '33'], 
            'nam' : ['Nahum', '34'], 'hab' : ['Habakkuk', '35'], 'zep' : ['Zephaniah', '36'], 'hag' : ['Haggai', '37'], 
            'zec' : ['Zechariah', '38'], 'mal' : ['Malachi', '39'],
            'mat' : ['Matthew', '41'], 'mrk' : ['Mark', '42'], 'luk' : ['Luke', '43'], 'jhn' : ['John', '44'], 
            'act' : ['Acts', '45'], 'rom' : ['Romans', '46'], '1co' : ['1 Corinthians', '47'], '2co' : ['2 Corinthians', '48'], 
            'gal' : ['Galatians', '49'], 'eph' : ['Ephesians', '50'], 'php' : ['Philippians', '51'], 'col' : ['Colossians', '52'], 
            '1th' : ['1 Thessalonians', '53'], '2th' : ['2 Thessalonians', '54'], '1ti' : ['1 Timothy', '55'], '2ti' : ['2 Timothy', '56'], 
            'tit' : ['Titus', '57'], 'phm' : ['Philemon', '58'], 'heb' : ['Hebrews', '59'], 'jas' : ['James', '60'], 
            '1pe' : ['1 Peter', '61'], '2pe' : ['2 Peter', '62'], '1jn' : ['1 John', '63'], '2jn' : ['2 John', '64'], 
            '3jn' : ['3 John', '65'], 'jud' : ['Jude', '66'], 'rev' : ['Revelation', '67'], 
            'tob' : ['Tobit', '68'], 'jdt' : ['Judith', '69'], 'esg' : ['Esther', '70'], 'wis' : ['Wisdom of Solomon', '71'], 
            'sir' : ['Sirach', '72'], 'bar' : ['Baruch', '73'], 'lje' : ['Letter of Jeremiah', '74'], 's3y' : ['Song of the Three Children', '75'], 
            'sus' : ['Susanna', '76'], 'bel' : ['Bel and the Dragon', '77'], '1ma' : ['1 Maccabees', '78'], '2ma' : ['2 Maccabees', '79'], 
            '3ma' : ['3 Maccabees', '80'], '4ma' : ['4 Maccabees', '81'], '1es' : ['1 Esdras', '82'], '2es' : ['2 Esdras', '83'], 
            'man' : ['Prayer of Manasses', '84'], 'ps2' : ['Psalms 151', '85'], 'oda' : ['Odae', '86'], 'pss' : ['Psalms of Solomon', '87'], 
            'jsa' : ['Joshua A', '88'], 'jdb' : ['Joshua B', '89'], 'tbs' : ['Tobit S', '90'], 'sst' : ['Susannah (Theodotion)', '91'], 
            'dnt' : ['Daniel (Theodotion)', '92'], 'blt' : ['Bel and the Dragon (Theodotion)', '93'], 
            'frt' : ['Front Matter', 'A0'], 'int' : ['Introductions', 'A7'], 'bak' : ['Back Matter', 'A1'], 
            'cnc' : ['Concordance', 'A8'], 'glo' : ['Glossary', 'A9'], 'tdx' : ['Topical Index', 'B0'], 'ndx' : ['Names Index', 'B1'], 
            'xxa' : ['Extra A', '94'], 'xxb' : ['Extra B', '95'], 'xxc' : ['Extra C', '96'], 'xxd' : ['Extra D', '97'],
            'xxe' : ['Extra E', '98'], 'xxf' : ['Extra F', '99'], 'xxg' : ['Extra G', '100'], 'oth' : ['Other', 'A2'], 
            'eza' : ['Apocalypse of Ezra', 'A4'], '5ez' : ['5 Ezra (Latin Prologue)', 'A5'], '6ez' : ['6 Ezra (Latin Epilogue)', 'A6'], 'dag' : ['Daniel Greek', 'B2'], 
            'ps3' : ['Psalms 152-155', 'B3'], '2ba' : ['2 Baruch (Apocalypse)', 'B4'], 'lba' : ['Letter of Baruch', 'B5'], 'jub' : ['Jubilees', 'B6'], 
            'eno' : ['Enoch', 'B7'], '1mq' : ['1 Meqabyan', 'B8'], '2mq' : ['2 Meqabyan', 'B9'], '3mq' : ['3 Meqabyan', 'C0'], 
            'rep' : ['Reproof (Proverbs 25-31)', 'C1'], '4ba' : ['4 Baruch (Rest of Baruch)', 'C2'], 'lao' : ['Laodiceans', 'C3'] 
          }


class Usfm (Component) :
    '''This class contains information about a type of component 
    used in a type of project.'''

    def __init__(self, project, config) :
        super(Usfm, self).__init__(project, config)

        self.compIDs = compIDs
        self.project = project
        self.defaultRenderer = 'xetex'
        self.defaultSourceType = 'paratext'
        self.defaultStyleFile = 'usfm.sty'
        self.ptProjectInfoFile = os.path.join('gather', getPtId() + '.ssf')
#        self.usfmManagers = ['source', 'font', 'preprocess', 'style', 'illustration', 'hyphenation']
        self.usfmManagers = ['font']

# Manager Descrption
#    source - Locate component source file, copy or link to project if needed
#    font - Manage fonts for all component types and renderers
#    preprocess - Create the process file, do any preprocesses needed
#    style - Manage element styles
#    illustration - Manage illustrations for all component types and renderers
#    hyphenation - Manage hyphenation information for components according to renderer


#(02:40:10 PM) uniscript: so onto rpm?
#(02:41:27 PM) Dennis: Yes, 
#(02:41:58 PM) Dennis: So, I'm setting up comps and see that I want to run my managers from inside the comp, I think
#(02:42:13 PM) Dennis: I'm not sure how to do that
#(02:42:20 PM) Dennis: or if I want to
#(02:42:37 PM) uniscript: ask the project to get the manager for you
#(02:43:02 PM) uniscript: I doubt you want to 'run' a manager so much as query it or have it do some calculation for you and return the (string) result
#(02:43:05 PM) Dennis: But different comps will need the manager to act differently
#(02:43:26 PM) uniscript: for example?
#(02:43:57 PM) Dennis: thinking...
#(02:45:04 PM) Dennis: Ok, if I have a type of project that has types of components, wouldn't I need to load the managers when I get to the component level?
#(02:45:30 PM) uniscript: just have the component ask the project for the manager
#(02:45:31 PM) Dennis: Or, should I load every possible manager at the project level?
#(02:45:36 PM) uniscript: the project loads it if it hasn't done so already
#(02:46:16 PM) uniscript: the project passes the manager to the component, who does not keep hold of a reference to it in self.something
#(02:46:20 PM) uniscript: note the NOT there
#(02:46:24 PM) Dennis: Ok, so I will move all the manager info up to book, which is a type of project
#(02:46:34 PM) uniscript: and the component can now query or tell the manager to do something
#(02:46:39 PM) uniscript: yes
#(02:46:43 PM) uniscript: no
#(02:46:44 PM) uniscript: err
#(02:47:11 PM) uniscript: a component will say to the book project: I need the mainfont manager
#(02:47:22 PM) uniscript: since the component knows that its font manager is called mainfont
#(02:47:29 PM) uniscript: because we told it that as part of its config
#(02:47:46 PM) uniscript: the project will go "oh yeh I have one of those around here someplace, here go you"
#(02:48:00 PM) uniscript: and then the component can bug that poor manager silly
#(02:49:40 PM) Dennis: I think I've drifted from task specific managers to more generalized ones. For example, the font manager would handle font for all possible renderers in the system
#(02:49:52 PM) uniscript: no
#(02:49:53 PM) Dennis: Is that not a good direction
#(02:50:15 PM) uniscript: well yes ok it could
#(02:50:36 PM) uniscript: but a single font manager is not going to hold all the font configuration for all of the components in a  project
#(02:50:48 PM) Dennis: true
#(02:50:54 PM) uniscript: and it's up to you if you have a tex specific font manager
#(02:51:02 PM) uniscript: subclassing a generic font manager
#(02:51:08 PM) uniscript: or you have a generic font manager
#(02:51:18 PM) uniscript: it depends how clever you want to make your manager
#(02:51:34 PM) uniscript: the issue is that you don't try to just have one manager store everything
#(02:51:46 PM) uniscript: if different components can have different configurations for a manager
#(02:51:52 PM) uniscript: then you need different managers of the same type
#(02:51:58 PM) Dennis: the font manager would be able to know what the renderer is and then produce the needed output
#(02:52:29 PM) uniscript: given the project would create a font manager of the correct type, I suppose, yes
#(02:52:49 PM) uniscript: but remember a map may want the same font manager to output very different info from a usfm book
#(02:53:01 PM) Dennis: true
#(02:53:42 PM) uniscript: want a car image?
#(02:53:45 PM) Dennis: so you are suggesting that I create lots of little managers that are very task specific, right?
#(02:53:50 PM) uniscript: front wheels are components with breaks
#(02:53:54 PM) uniscript: as are back wheels
#(02:54:13 PM) uniscript: front and back wheels are subtly different and they will have different break managers
#(02:54:28 PM) uniscript: notice that back wheels will be told to stop by both the foot and the hand break
#(02:54:34 PM) Dennis: that helps :-)
#(02:54:37 PM) uniscript: only the font wheels are only stopped with the foot break
#(02:54:54 PM) uniscript: so breaks need to be able to stop with either foot or hand break
#(02:55:04 PM) uniscript: even though front breaks will never be told to stop with a hand break
#(02:55:46 PM) uniscript: so we have 2 classes: wheels (components), breaks (manager)
#(02:55:50 PM) Dennis: so lots of little managers that all get loaded at the project level and are called by the components as needed
#(02:56:02 PM) uniscript: but 4 instances: front wheel, back wheel, front break, back break
#(02:56:07 PM) uniscript: right
#(02:56:31 PM) uniscript: basically, shared config between components should go into a manager
#(02:57:01 PM) Dennis: so calling a manager would be something like:
#self.project.thisManager('var')
#(02:57:06 PM) uniscript: thus stylesheet is a manager
#(02:57:28 PM) uniscript: self.project.createManager(self.cfg['managers']['font'])
#(02:58:09 PM) Dennis: Oh, I remember that, not sure if I have my head around that yet
#(02:58:35 PM) Dennis: I'll need to play around with the config structure to see the data flow
#(02:58:42 PM) uniscript: ok
#(02:59:49 PM) Dennis: I'll try to sum this up in notes in my code and think about it more as I pedal home
#(02:59:59 PM) Dennis: Hopefully something will click
#(03:00:06 PM) uniscript: ok, we can take another bite on Monday
#(03:00:34 PM) Dennis: I just want to be sure I don't head the wrong direction and have to do a rewrite, that's my biggest fear
#(03:00:44 PM) uniscript: yup
#(03:01:22 PM) Dennis: So should I be doing all the manager loading in the project type (book.py) module when it inits?
#(03:01:38 PM) uniscript: don't know
#(03:01:44 PM) uniscript: at the moment it makes no difference
#(03:01:56 PM) uniscript: since everything will ask for what it wants and you can load it then
#(03:02:15 PM) uniscript: there's nothing to be gained by preloading
#(03:02:25 PM) uniscript: so probably not
#(03:02:31 PM) Dennis: hmm, yes, and you are calling for basically custom, on-the-fly managers
#(03:02:35 PM) uniscript: why load the map fonts when you are rendering james?
#(03:02:45 PM) Dennis: yes, I see
#(03:03:51 PM) Dennis: So, I would be making all these little custom managers when the component type class is loading
#(03:04:48 PM) Dennis: I'll think about it, probably will need to talk more on Monday
#(03:04:55 PM) Dennis: thanks for your help
#(03:04:55 PM) uniscript: nw


        # Init the managers
        for manager in self.usfmManagers :
            self.project.createManager(manager)


    def render(self) :
        '''Does USFM specific rendering of a USFM component'''
        #useful variables: self.project, self.cfg

        # Is this a valid component ID for this component type?
        if self.cfg['name'] in self.compIDs :
            terminal("Rendering: " + self.compIDs[self.cfg['name']][0])

        # Determine the renderer
        renderer = testForSetting(self.cfg, 'renderer')
        if not renderer :
            renderer = self.defaultRenderer

        # Check for source
        sourceFile = testForSetting(self.cfg, 'sourceFile')
        if not sourceFile :
            pass #sourceFile = howdowecallthesourcemanager?(sourceType)
            






