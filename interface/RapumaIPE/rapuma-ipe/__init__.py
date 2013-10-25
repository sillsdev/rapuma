# -*- coding: utf-8 -*-

from gi.repository import GObject, Gtk, Gedit

UI_XML = """<ui>
<menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_3">
        <menuitem name="ExampleAction" action="ExampleAction"/>
      </placeholder>
    </menu>
</menubar>
</ui>"""

class RapumaIPE (GObject.Object, Gedit.WindowActivatable) :
    __gtype_name__ = "RapumaIPE"
    window = GObject.property(type=Gedit.Window)
   
    def __init__(self):
        GObject.Object.__init__(self)
    
    def _add_ui(self):
        manager = self.window.get_ui_manager()
        self._actions = Gtk.ActionGroup("RapumaIPE")
        self._actions.add_actions([
            ('ExampleAction', Gtk.STOCK_INFO, "RapumaIPE", 
                None, "Say hello to the current document", 
                self.on_example_action_activate),
        ])
        manager.insert_action_group(self._actions)
        self._ui_merge_id = manager.add_ui_from_string(UI_XML)
        manager.ensure_update()
        
    def do_activate(self):
        self._add_ui()

    def do_deactivate(self):
        self._remove_ui()

    def do_update_state(self):
        pass
    
    def on_example_action_activate(self, action, data=None):
        view = self.window.get_active_view()
        if view:
            view.get_buffer().insert_at_cursor("Hello world from Rapuma!")
        
    def _remove_ui(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self._ui_merge_id)
        manager.remove_action_group(self._actions)
        manager.ensure_update()
        
        
