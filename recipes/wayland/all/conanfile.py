from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os


class WaylandConan(ConanFile):
    name = "wayland"
    description = "Wayland is a project to define a protocol for a compositor to talk to its clients as well as a library implementation of the protocol"
    topics = ("conan", "wayland")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://wayland.freedesktop.org"
    license = "MIT"
    generators = "pkg_config"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_libraries": [True, False],
        "enable_dtd_validation": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_libraries": True,
        "enable_dtd_validation": True,
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _meson = None

    def requirements(self):
        if self.options.enable_libraries:
            self.requires("libffi/3.3")
        if self.options.enable_dtd_validation:
            self.requires("libxml2/2.9.10")
        self.requires("expat/2.2.9")

    def build_requirements(self):
        self.build_requires('meson/0.54.2')

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Wayland can be built on Linux only")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "wayland-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        tools.replace_in_file(os.path.join(self._source_subfolder, 'meson.build'), "subdir('tests')", "#subdir('tests')")

    def _configure_meson(self):
        if not self._meson:
            self._meson = Meson(self)
            self._meson.configure(source_folder= self._source_subfolder, build_folder=self._build_subfolder, defs={
                'libraries': 'true' if self.options.enable_libraries else 'false',
                'dtd_validation': 'true' if self.options.enable_dtd_validation else 'false',
                'documentation': 'false',
            })
        return self._meson

    def build(self):
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

