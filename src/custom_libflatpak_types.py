from __future__ import annotations
from gi.repository import Gio, Gtk, GLib, Gdk, Flatpak
import gettext, subprocess

_ = gettext.gettext

class WhInstallation:
	real_installation = None
	remotes = None
	packages = None
	app_icon_path = ""
	cli_format = ""

	def __init__(self, installation):
		self.real_installation = installation
		self.remotes = []
		self.packages = []
		self.app_icon_path = f"{installation.get_path().get_path()}/exports/share/icons"

		for remote in installation.list_remotes():
			self.remotes.append(WhRemote(self, remote))

		for package in installation.list_installed_refs():
			wh_package = WhInstalledPackage(self, package)
			self.packages.append(wh_package)
			origin = wh_package.real_package.get_origin()
			for remote in self.remotes:
				if remote.real_remote.get_name() == origin:
					wh_package.remote = remote
					break

		match inst_id := installation.get_id():
			case "default": self.cli_format = "--system"
			case "user": self.cli_format = "--user"
			case __: self.cli_format = f"--installation={inst_id}"

class WhRemote:
	installation = None
	real_remote = None

	def get_packages(self):
		return list(filter(
			lambda package: package.real_package.get_origin() == self.real_remote.get_name(),
			self.installation.packages
		))

	def __init__(self, installation, remote):
		self.installation = installation
		self.real_remote = remote

class WhInstalledPackage:
	installation = None
	remote = None
	real_package = None
	is_runtime = False

	def __init__(self, installation, installed_ref):
		self.installation = installation
		self.real_package = installed_ref
		self.is_runtime = installed_ref.get_kind() == Flatpak.RefKind.RUNTIME
