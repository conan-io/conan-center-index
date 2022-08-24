from conans import ConanFile, Meson, tools
from conan.errors import ConanInvalidConfiguration
import os


class AtSpi2CoreConan(ConanFile):
    name = "at-spi2-core"
    description = "It provides a Service Provider Interface for the Assistive Technologies available on the GNOME platform and a library against which applications can be linked"
    topics = "atk", "accessibility"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.gnome.org/GNOME/at-spi2-core/"
    license = "LGPL-2.1-or-later"
    generators = "pkg_config"

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
        tools.files.get(self, **self.conan_data["sources"][self.version],
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
            tools.files.patch(self, **patch)
        if tools.Version(self.version) >= "2.42.0":
            tools.replace_in_file(os.path.join(self._source_subfolder, "bus", "meson.build"),
                                  "if x11_dep.found()",
                                  "if x11_option == 'yes'")
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "etc"))


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ["include/at-spi-2.0"]
        self.cpp_info.names["pkg_config"] = "atspi-2"

    def package_id(self):
        self.info.requires["glib"].full_package_mode()
