from gi.repository import Adw, Gtk, GLib#, Gio, Pango
from .host_info import HostInfo
from .app_row import AppRow
from .error_toast import ErrorToast
from .properties_page import PropertiesPage

@Gtk.Template(resource_path="/io/github/flattool/Warehouse/packages_page/packages_page.ui")
class PackagesPage(Adw.BreakpointBin):
    __gtype_name__ = 'PackagesPage'
    gtc = Gtk.Template.Child
    packages_toast_overlay = gtc()
    scrolled_window = gtc()
    sidebar_button = gtc()
    refresh_button = gtc()
    search_bar = gtc()
    search_entry = gtc()
    packages_split = gtc()
    packages_list_box = gtc()
    refresh_status = gtc()

    # Referred to in the main window
    #    It is used to determine if a new page should be made or not
    #    This must be set to the created object from within the class's __init__ method
    instance = None

    def generate_list(self, *args):
        self.packages_list_box.remove_all()
        for package in HostInfo.flatpaks:
            row = AppRow(package)
            row.masked_status_icon.set_visible(package.is_masked)
            row.pinned_status_icon.set_visible(package.is_pinned)
            row.eol_package_package_status_icon.set_visible(package.is_eol)
            try:
                if not package.is_runtime:
                    row.eol_runtime_status_icon.set_visible(package.dependant_runtime.is_eol)
            except Exception as e:
                self.packages_toast_overlay.add_toast(ErrorToast(_("Error getting Flatpak '{}'").format(package.info["name"]), str(e)).toast)
            self.packages_list_box.append(row)

        first_row = self.packages_list_box.get_row_at_index(0)
        self.packages_list_box.select_row(first_row)
        self.properties_page.set_properties(first_row.package)
        self.scrolled_window.set_vadjustment(Gtk.Adjustment.new(0,0,0,0,0,0)) # Scroll list to top
        if self.packages_toast_overlay.get_child() != self.packages_split:
            self.packages_toast_overlay.set_child(self.packages_split)

    def row_select_handler(self, list_box, row):
        self.properties_page.set_properties(row.package)
        # if self.packages_split.get_collapsed():
        self.packages_split.set_show_content(True)

    def filter_func(self, row):
        search_text = self.search_entry.get_text().lower()
        title = row.get_title().lower()
        subtitle = row.get_subtitle().lower()
        if search_text in title or search_text in subtitle:
            return True

    def __init__(self, main_window, **kwargs):
        super().__init__(**kwargs)

        # Extra Object Creation
        self.main_window = main_window
        self.properties_page = PropertiesPage(main_window)

        # Apply
        HostInfo.get_flatpaks(callback=self.generate_list)

        self.packages_list_box.set_filter_func(self.filter_func)
        self.packages_split.set_content(self.properties_page)
        self.__class__.instance = self

        # Connections
        main_window.main_split.connect("notify::show-sidebar", lambda sidebar, *_: self.sidebar_button.set_visible(sidebar.get_collapsed() or not sidebar.get_show_sidebar()))
        main_window.main_split.connect("notify::collapsed", lambda sidebar, *_: self.sidebar_button.set_visible(sidebar.get_collapsed() or not sidebar.get_show_sidebar()))
        self.sidebar_button.connect("clicked", lambda *_: main_window.main_split.set_show_sidebar(True))
        
        self.refresh_button.connect("clicked", lambda *_: self.packages_toast_overlay.set_child(self.refresh_status))
        self.refresh_button.connect("clicked", lambda *_: HostInfo.get_flatpaks(callback=self.generate_list))

        self.search_entry.connect("search-changed", lambda *_: self.packages_list_box.invalidate_filter())
        self.search_bar.set_key_capture_widget(main_window)
        self.packages_list_box.connect("row-activated", self.row_select_handler)
