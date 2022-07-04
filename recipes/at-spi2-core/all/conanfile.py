from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os


class AtSpi2CoreConan(ConanFile):
    name = "at-spi2-core"
    description = "It provides a Service Provider Interface for the Assistive Technologies available on the GNOME platform and a library against which applications can be linked"
    topics = ("atk", "accessibility")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.gnome.org/GNOME/at-spi2-core/"
    license = "LGPL-2.1-or-later"
    generators = "pkg_config"

    provides = "at-spi2-atk", "atk"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_x11": [True, False],
        }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_x11": False,
        }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    _meson = None

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            self.options["glib"].shared = True

    def build_requirements(self):
        self.build_requires("meson/0.62.2")
        self.build_requires("pkgconf/1.7.4")

    def requirements(self):
        self.requires("glib/2.73.0")
        if self.options.with_x11:
            self.requires("xorg/system")
        self.requires("dbus/1.12.20")

    def validate(self):
        if self.options.shared and not self.options["glib"].shared:
            raise ConanInvalidConfiguration(
                "Linking a shared library against static glib can cause unexpected behaviour."
            )
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("only linux is supported by this recipe")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                    strip_root=True, destination=self._source_subfolder)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        defs = {}
        defs["introspection"] = "no"
        defs["docs"] = "false"
        defs["x11"] = "yes" if self.options.with_x11 else "no"
        args=[]
        args.append("--datadir=%s" % os.path.join(self.package_folder, "res"))
        args.append("--localedir=%s" % os.path.join(self.package_folder, "res"))
        args.append("--wrap-mode=nofallback")
        self._meson.configure(defs=defs, build_folder=self._build_subfolder, source_folder=self._source_subfolder, pkg_config_paths=".", args=args)
        return self._meson

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "bus", "meson.build"),
                                "if x11_dep.found()",
                                "if x11_option == 'yes'")
        tools.replace_in_file(os.path.join(self._source_subfolder, 'meson.build'),
            "subdir('tests')",
            "#subdir('tests')")
        tools.replace_in_file(os.path.join(self._source_subfolder, 'meson.build'),
            "libxml_dep = dependency('libxml-2.0', version: libxml_req_version)",
            "#libxml_dep = dependency('libxml-2.0', version: libxml_req_version)")
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))


    def package_info(self):
        self.cpp_info.components["atspi"].libs = ['atspi']
        self.cpp_info.components["atspi"].includedirs = ["include/at-spi-2.0"]
        self.cpp_info.components["atspi"].requires = ["dbus::dbus", "glib::glib"]
        self.cpp_info.components["atspi"].names["pkg_config"] = "atspi-2"
        
        self.cpp_info.components["atk"].libs = ["atk-1.0"]
        self.cpp_info.components["atk"].includedirs = ['include/atk-1.0']
        self.cpp_info.components["atk"].requires = ["glib::glib"]
        self.cpp_info.components["atk"].names['pkg_config'] = 'atk'

        self.cpp_info.components["atk-bridge"].libs = ['atk-bridge-2.0']
        self.cpp_info.components["atk-bridge"].includedirs = [os.path.join('include', 'at-spi2-atk', '2.0')]
        self.cpp_info.components["atk-bridge"].requires = ["dbus::dbus", "atk", "glib::glib", "atspi"]
        self.cpp_info.components["atk-bridge"].names['pkg_config'] = 'atk-bridge-2.0'

    def package_id(self):
        self.info.requires["glib"].full_package_mode()
