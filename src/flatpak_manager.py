from gi.repository import Gio, Gtk, GLib, Gdk, Flatpak
from src.custom_libflatpak_types import WhInstallation, WhRemote, WhInstalledPackage
from src.gtk.error_toast import ErrorToast
import subprocess, os, pathlib
import gettext

_ = gettext.gettext
icon_theme = Gtk.IconTheme.new()
icon_theme.add_search_path(f"{pathlib.Path.home()}/.local/share/flatpak/exports/share/icons")
direction = Gtk.Image().get_direction()

class Private:
	installations = []
	remotes = []
	packages = []

class FlatpakManager:
	@classmethod
	def get_installations(this):
		return Private.installations

	@classmethod
	def get_package_from_format_ref(this, format_ref):
		for pack in Private.packages:
			if pack.real_package.format_ref() == format_ref:
				return pack
	
	@classmethod
	def get_runtime_for_package(this, package):
		try:
			response = subprocess.run([
				'flatpak-spawn', '--host',
				'flatpak', 'info', '--show-runtime',
				package.installation.cli_format,
				package.real_package.format_ref()
			], text=True, capture_output=True).stdout
			response = f"runtime/{response.strip()}"
			return this.get_package_from_format_ref(response)
		except Exception as e:
			print("FlatpakManager.get_runtime_for_package error:")
			print(str(e))
			return None

	@classmethod
	def get_sdk_for_package(this, package):
		try:
			response = subprocess.run([
				'flatpak-spawn', '--host',
				'flatpak', 'info', '--show-sdk',
				package.installation.cli_format,
				package.real_package.format_ref()
			], text=True, capture_output=True).stdout
			response = f"runtime/{response.strip()}"
			return this.get_package_from_format_ref(response)
		except Exception as e:
			print("FlatpakManager.get_sdk_for_package error:")
			print(str(e))
			return None

	@classmethod
	def setup(this):
		Private.installations.clear()
		Private.remotes.clear()
		Private.packages.clear()

		user_installation_path = ""
		if data_path := GLib.getenv('HOST_XDG_DATA_HOME'):
			user_installation_path = f"{data_path}/flatpak"
		else:
			user_installation_path = f"{GLib.get_home_dir()}/.local/share/flatpak"

		try:
			installations = Flatpak.get_system_installations()
			user_installation_location = Gio.File.new_for_path(user_installation_path)
			user_installation = Flatpak.Installation.new_for_path(user_installation_location, True)
			installations.append(user_installation)
			for inst in installations:
				wh_installation = WhInstallation(inst)
				icon_theme.add_search_path(wh_installation.app_icon_path)
				Private.installations.append(wh_installation)
				Private.remotes += wh_installation.remotes
				Private.packages += wh_installation.packages

			# for inst in Private.installations:
			# 	print("Installation: {")
			# 	print("  Name:", inst.real_installation.get_display_name())
			# 	print("  Path:", inst.real_installation.get_path().get_path())
			# 	print("  Remotes: [")
			# 	for rem in inst.remotes:
			# 		print("   ", rem.real_remote.get_title(), "|", rem.real_remote.get_name())
			# 	print("  ]")
			# 	print("  Packages: [")
			# 	for pack in inst.real_installation.list_installed_refs():
			# 		print("   ", pack.get_name() + ",")
			# 	print("  ]")
			# 	print("}")

			print("Dependant runtimes for com.discordapp.DiscordCanary:")
			print(this.get_runtime_for_package(this.get_package_from_format_ref('app/com.discordapp.DiscordCanary/x86_64/beta')).real_package.format_ref())
			print(this.get_sdk_for_package(this.get_package_from_format_ref('app/com.discordapp.DiscordCanary/x86_64/beta')).real_package.format_ref())
			return user_installation

		except Exception as e:
			print(e)
			raise e

		# print(user_installation.list_installed_refs())
