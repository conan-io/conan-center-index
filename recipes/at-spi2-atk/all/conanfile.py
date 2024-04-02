from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, rmdir

from conans import Meson
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
    deprecated = "at-spi2-core"

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


    def build_requirements(self):
        self.build_requires("meson/1.1.1")
        self.build_requires('pkgconf/1.9.3')

    def requirements(self):
        self.requires("at-spi2-core/2.44.1")
        self.requires("atk/2.38.0")
        self.requires("glib/2.76.3")
        self.requires("libxml2/2.11.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
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
        rmdir(self, os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = ['atk-bridge-2.0']
        self.cpp_info.includedirs = [os.path.join('include', 'at-spi2-atk', '2.0')]
        self.cpp_info.names['pkg_config'] = 'atk-bridge-2.0'
