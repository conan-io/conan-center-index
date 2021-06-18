from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os


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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires('meson/0.57.1')
        self.build_requires('pkgconf/1.7.3')

    def requirements(self):
        self.requires('at-spi2-core/2.39.1')
        self.requires('atk/2.36.0')
        self.requires('glib/2.67.6')
        self.requires('libxml2/2.9.10')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

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
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = [os.path.join('include', 'at-spi2-atk', '2.0')]
        self.cpp_info.names['pkg_config'] = 'atk-bridge-2.0'
