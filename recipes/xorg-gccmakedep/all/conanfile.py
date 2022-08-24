from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import os
import re

required_conan_version = ">=1.33.0"


class XorgGccmakedep(ConanFile):
    name = "xorg-gccmakedep"
    description = "script to create dependencies in makefiles using 'gcc -M'"
    topics = ("xorg", "gcc", "dependency", "obsolete")
    license = "MIT"
    homepage = "https://gitlab.freedesktop.org/xorg/util/gccmakedep"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

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

    def build_requirements(self):
        self.build_requires("pkgconf/1.7.4")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows is not supported by xorg-gccmakedep")

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
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure(configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        conf_ac_text = tools.files.load(self, os.path.join(self._source_subfolder, "configure.ac"))
        topblock = re.match("((?:dnl[^\n]*\n)+)", conf_ac_text, flags=re.MULTILINE).group(1)
        license_text = re.subn(r"^dnl(|\s+([^\n]*))", r"\1", topblock, flags=re.MULTILINE)[0]
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), license_text)

        autotools = self._configure_autotools()
        autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libdirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
