from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import os
import re

required_conan_version = ">=1.33.0"


class XorgMakedepend(ConanFile):
    name = "xorg-makedepend"
    description = "Utility to parse C source files to make dependency lists for Makefiles"
    topics = ("xorg", "dependency", "obsolete")
    license = "MIT"
    homepage = "https://gitlab.freedesktop.org/xorg/util/cf"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "patches/*"
    generators = "pkg_config"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires("xorg-macros/1.19.3")
        self.requires("xorg-proto/2021.4")

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows is not supported by xorg-makedepend")

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=self._settings_build.os == "Windows")
        self._autotools.libs = []
        self._autotools.configure(configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        def_h_text = tools.load(os.path.join(self._source_subfolder, "def.h"))
        license_text = next(re.finditer(r"/\*([^*]+)\*/", def_h_text)).group(1)
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), license_text)

        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libdirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
