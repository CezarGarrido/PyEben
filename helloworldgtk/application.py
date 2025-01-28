from gi import require_versions
require_versions({"Gtk": "3.0"})
from gi.repository import Gtk
from .window import Window


class Application(Gtk.Application):

    def __init__(self):
        super().__init__()

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        win = Window(self)
        win.show_all()
        win.present()
