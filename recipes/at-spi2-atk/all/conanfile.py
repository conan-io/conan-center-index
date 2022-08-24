from conans import ConanFile, Meson, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class AtSPI2AtkConan(ConanFile):
    name = "at-spi2-atk"
    description = "library that bridges ATK to At-Spi2 D-Bus service."
    topics = ("conan", "atk", "accessibility")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.gnome.org/GNOME/at-spi2-atk"
    license = "LGPL-2.1-or-later"
    generators = "pkg_config"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        }
    default_options = {
        "shared": False,
        "fPIC": True,
        }

    _meson = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def validate(self):
        if self.settings.os not in ("Linux", "FreeBSD"):
            raise ConanInvalidConfiguration("at-spi2-atk is only supported on Linux and FreeBSD")
        if self.options.shared and (not self.options["glib"].shared
                                    or not self.options["at-spi2-core"].shared
                                    or not self.options["atk"].shared):
            raise ConanInvalidConfiguration(
                "Linking a shared library against static glib can cause unexpected behaviour."
            )


    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            self.options["at-spi2-core"].shared = True
            self.options["atk"].shared = True
            self.options["glib"].shared = True


    def build_requirements(self):
        self.build_requires("meson/0.62.2")
        self.build_requires('pkgconf/1.7.4')

    def requirements(self):
        self.requires("at-spi2-core/2.44.1")
        self.requires("atk/2.38.0")
        self.requires("glib/2.73.0")
        self.requires("libxml2/2.9.14")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_meson(self):
        if self._meson:
            return self._meson
        self._meson = Meson(self)
        args=[]
        args.append('--wrap-mode=nofallback')
        self._meson.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder, pkg_config_paths='.', args=args)
        return self._meson

    def build(self):
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = [os.path.join('include', 'at-spi2-atk', '2.0')]
        self.cpp_info.names['pkg_config'] = 'atk-bridge-2.0'

    def package_id(self):
        self.info.requires["at-spi2-core"].full_package_mode()
        self.info.requires["atk"].full_package_mode()
        self.info.requires["glib"].full_package_mode()
