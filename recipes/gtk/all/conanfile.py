from conan import ConanFile
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc
from conan.tools.files import get, copy, rmdir, rm
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.4"


class GtkConan(ConanFile):
    name = "gtk"
    description = "libraries used for creating graphical user interfaces for applications."
    topics = ("gtk", "widgets")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gtk.org"
    license = "LGPL-2.1-or-later"
    package_type = "library"
    languages = "C"
    settings = "os", "arch", "compiler", "build_type"
    implements = ["auto_shared_fpic"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_wayland": [True, False],
        "with_x11": [True, False],
        "with_gstreamer": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_wayland": False,
        "with_x11": False,
        "with_gstreamer": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # Fix duplicate definitions of DllMain
            self.options["gdk-pixbuf"].shared = True
            # Fix segmentation fault
            self.options["cairo"].shared = True
            # TODO: Re-check if this is still needed for gtk4
            # The upstream meson file does not create a static library
            # See https://github.com/GNOME/gtk/commit/14f0a0addb9a195bad2f8651f93b95450b186bd6
            self.options.shared = True
        if self.settings.os != "Linux":
            del self.options.with_wayland
            del self.options.with_x11

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        self.tool_requires("cmake/[>=3.17]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

        # TODO: Re-check if these are needed for gtk4
        #if self._gtk4:
        #    self.build_requires("libxml2/2.9.14") # for xmllint
        #
        #if self._gtk4:
        #    self.build_requires("sassc/3.6.2")

    def requirements(self):
        self.requires("gdk-pixbuf/[^2.42]")
        self.requires("glib/[^2.82]", override=True) # gtk requires >=2.82
        #if not is_msvc(self):
        #    self.requires("cairo/[>=1.17.4 <2]")

            #self.requires("graphene/1.10.8")
            #self.requires("fribidi/1.0.12")
            #self.requires("libpng/1.6.37")
            #self.requires("libtiff/4.3.0")
            #self.requires("libjpeg/9d")
        if self.settings.os == "Linux":
            self.requires("xkbcommon/[>=1.5.0 <2]")
            if self.options.with_wayland:
                self.requires("wayland/[>1.22.0 <2]")
            if self.options.with_x11:
                self.requires("xorg/system")
        self.requires("libepoxy/1.5.10")
        self.requires("pango/[>1.50.7 <2]")
        if self.options.with_gstreamer:
            self.requires("gstreamer/[>=1.19.2 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        if self.settings.os == "Linux":
            true_false = lambda opt : "true" if opt else "false" 
            tc.project_options["wayland-backend"] = true_false(self.options.with_wayland)
            tc.project_options["x11-backend"] = true_false(self.options.with_x11)
        tc.project_options["introspection"] = "disabled"
        tc.project_options["documentation"] = "false"
        tc.project_options["man-pages"] = "false"
        tc.project_options["build-testsuite"] = "false"
        tc.project_options["build-tests"] = "false"
        tc.project_options["build-examples"] = "false"
        tc.project_options["build-demos"] = "false"
        
        enabled_disabled = lambda opt : "enabled" if opt else "disabled" 
        tc.project_options["media-gstreamer"] = enabled_disabled(self.options.with_gstreamer)
        tc.generate()

        #args=[]
        #args.append("--wrap-mode=nofallback")
    
        deps = PkgConfigDeps(self)
        deps.generate()
    
    def validate(self):
        # TODO: Re-validate these cases
        if is_msvc(self) and not self.dependencies["gdk-pixbuf"].options.shared:
                raise ConanInvalidConfiguration("MSVC build requires shared gdk-pixbuf")
        if is_msvc(self) and not self.dependencies["cairo"].options.shared:
            raise ConanInvalidConfiguration("MSVC build requires shared cairo")

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        
        meson = Meson(self)
        meson.install()
        
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        if False: # TODO revisit for gtk4
            self.cpp_info.components["gdk-3.0"].libs = ["gdk-3"]
            self.cpp_info.components["gdk-3.0"].includedirs = [os.path.join("include", "gtk-3.0")]
            self.cpp_info.components["gdk-3.0"].requires = []
            if self.options.with_pango:
                self.cpp_info.components["gdk-3.0"].requires.extend(["pango::pango_", "pango::pangocairo"])
            self.cpp_info.components["gdk-3.0"].requires.append("gdk-pixbuf::gdk-pixbuf")
            if self.settings.compiler != "Visual Studio":
                self.cpp_info.components["gdk-3.0"].requires.extend(["cairo::cairo", "cairo::cairo-gobject"])
            if self.settings.os == "Linux":
                self.cpp_info.components["gdk-3.0"].requires.extend(["glib::gio-unix-2.0", "cairo::cairo-xlib"])
                if self.options.with_x11:
                    self.cpp_info.components["gdk-3.0"].requires.append("xorg::xorg")
            self.cpp_info.components["gdk-3.0"].requires.append("libepoxy::libepoxy")
            self.cpp_info.components["gdk-3.0"].names["pkg_config"] = "gdk-3.0"

            self.cpp_info.components["gtk+-3.0"].libs = ["gtk-3"]
            self.cpp_info.components["gtk+-3.0"].requires = ["gdk-3.0", "atk::atk"]
            if self.settings.compiler != "Visual Studio":
                self.cpp_info.components["gtk+-3.0"].requires.extend(["cairo::cairo", "cairo::cairo-gobject"])
            self.cpp_info.components["gtk+-3.0"].requires.extend(["gdk-pixbuf::gdk-pixbuf", "glib::gio-2.0"])
            if self.settings.os == "Linux":
                self.cpp_info.components["gtk+-3.0"].requires.append("at-spi2-atk::at-spi2-atk")
            self.cpp_info.components["gtk+-3.0"].requires.append("libepoxy::libepoxy")
            if self.options.with_pango:
                self.cpp_info.components["gtk+-3.0"].requires.append('pango::pangoft2')
            if self.settings.os == "Linux":
                self.cpp_info.components["gtk+-3.0"].requires.append("glib::gio-unix-2.0")
            self.cpp_info.components["gtk+-3.0"].includedirs = [os.path.join("include", "gtk-3.0")]
            self.cpp_info.components["gtk+-3.0"].names["pkg_config"] = "gtk+-3.0"

            self.cpp_info.components["gail-3.0"].libs = ["gailutil-3"]
            self.cpp_info.components["gail-3.0"].requires = ["gtk+-3.0", "atk::atk"]
            self.cpp_info.components["gail-3.0"].includedirs = [os.path.join("include", "gail-3.0")]
            self.cpp_info.components["gail-3.0"].names["pkg_config"] = "gail-3.0"
            
        self.cpp_info.names["pkg_config"] = "gtk4"
        self.cpp_info.libs = ["gtk-4"]
        self.cpp_info.includedirs.append(os.path.join("include", "gtk-4.0"))
