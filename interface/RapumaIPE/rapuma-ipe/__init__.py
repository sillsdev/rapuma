# -*- coding: utf-8 -*-

# Much of the code here taken from:
#   http://www.micahcarrick.com/writing-plugins-for-gedit-3-in-python.html



########################################################################
# Example #4 - Inserting Menu Items

#from gi.repository import GObject, Gtk, Gedit

#UI_XML = """<ui>
#<menubar name="MenuBar">
    #<menu name="ToolsMenu" action="Tools">
      #<placeholder name="ToolsOps_3">
        #<menuitem name="ExampleAction" action="ExampleAction"/>
      #</placeholder>
    #</menu>
#</menubar>
#</ui>"""

#class RapumaIPE (GObject.Object, Gedit.WindowActivatable) :
    #__gtype_name__ = "RapumaIPE"
    #window = GObject.property(type=Gedit.Window)
   
    #def __init__(self):
        #GObject.Object.__init__(self)
    
    #def _add_ui(self):
        #manager = self.window.get_ui_manager()
        #self._actions = Gtk.ActionGroup("RapumaIPE")
        #self._actions.add_actions([
            #('ExampleAction', Gtk.STOCK_INFO, "RapumaIPE", 
                #None, "Say hello to the current document", 
                #self.on_example_action_activate),
        #])
        #manager.insert_action_group(self._actions)
        #self._ui_merge_id = manager.add_ui_from_string(UI_XML)
        #manager.ensure_update()
        
    #def do_activate(self):
        #self._add_ui()

    #def do_deactivate(self):
        #self._remove_ui()

    #def do_update_state(self):
        #pass
    
    #def on_example_action_activate(self, action, data=None):
        #view = self.window.get_active_view()
        #if view:
            #view.get_buffer().insert_at_cursor("Hello world from Rapuma!")
        
    #def _remove_ui(self):
        #manager = self.window.get_ui_manager()
        #manager.remove_ui(self._ui_merge_id)
        #manager.remove_action_group(self._actions)
        #manager.ensure_update()
        
########################################################################


########################################################################
# Example #5 - Adding Bottom and Side Panels

#from gi.repository import GObject, Gtk, Gedit

#class ExamplePlugin05(GObject.Object, Gedit.WindowActivatable):
    #__gtype_name__ = "RapumaIPE"
    #window = GObject.property(type=Gedit.Window)
   
    #def __init__(self):
        #GObject.Object.__init__(self)
        
    #def do_activate(self):
        #icon = Gtk.Image.new_from_stock(Gtk.STOCK_YES, Gtk.IconSize.MENU)
        #self._side_widget = Gtk.Label("This is the side panel.")
        #panel = self.window.get_side_panel()
        #panel.add_item(self._side_widget, "ExampleSidePanel", "RapumaIPE", icon)
        #panel.activate_item(self._side_widget)

    #def do_deactivate(self):
        #panel = self.window.get_side_panel()
        #panel.remove_item(self._side_widget)

    #def do_update_state(self):
        #pass

########################################################################


########################################################################
# Example #6 - Configure Dialog

from gi.repository import GObject, Gtk, Gedit, PeasGtk

class ExamplePlugin06(GObject.Object, Gedit.AppActivatable, PeasGtk.Configurable):
    __gtype_name__ = "RapumaIPE"
    window = GObject.property(type=Gedit.Window)
   
    def __init__(self):
        GObject.Object.__init__(self)
        
    def do_activate(self):
        pass
    
    def do_create_configure_widget(self):
        widget = Gtk.CheckButton("A configuration setting.")
        widget.set_border_width(6)
        return widget
        
    def do_deactivate(self):
        pass

    def do_update_state(self):
        pass

########################################################################
