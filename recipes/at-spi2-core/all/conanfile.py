from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
    
    def build_requirements(self):
        self.build_requires("meson/0.59.1")
        self.build_requires("pkgconf/1.7.4")
    
    def requirements(self):
        self.requires("glib/2.70.0")
        if self.options.with_x11:
            self.requires("xorg/system")
        self.requires("dbus/1.12.20")

    def validate(self):
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
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ["include/at-spi-2.0"]
        self.cpp_info.names["pkg_config"] = "atspi-2"

