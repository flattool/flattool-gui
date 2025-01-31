from gi.repository import Gio, Gtk, GLib, Gdk, Flatpak
from src.gtk.error_toast import ErrorToast
from src.flatpak_manager import FlatpakManager
from src.custom_libflatpak_types import WhInstallation, WhRemote, WhInstalledPackage
import subprocess, os, pathlib
import gettext

_ = gettext.gettext
home = f"{pathlib.Path.home()}"

class HostInfo:
	home = home
	clipboard = Gdk.Display.get_default().get_clipboard()
	main_window = None
	snapshots_path = f"{home}/.var/app/io.github.flattool.Warehouse/data/Snapshots/"

	@classmethod
	def setup(this, callback=None):
		# Gio.Task.new(None, None, None).run_in_thread(lambda *_args: FlatpakManager.setup())
		FlatpakManager.setup()
		system_inst = FlatpakManager.get_installations()[0].real_installation
		new_rem = Flatpak.Remote.new("app_center")
		new_rem.set_title("App Center")
		new_rem.set_url("https://flatpak.elementary.io/repo.flatpakrepo")
		system_inst.add_remote(new_rem, False, None)