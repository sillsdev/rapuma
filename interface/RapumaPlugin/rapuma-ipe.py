#!/usr/bin/python

from gi.repository import GObject, Gtk, Gdk, Gedit

class RapumaIPE(gedit.Plugin):
    def __init__(self):
        print "Plugin loaded"

    def activate(self, window):
        print "Plugin activated"

    def deactivate(self, window):
        print "Plugin deactivated"

    def update_ui(self, window):
        pass
