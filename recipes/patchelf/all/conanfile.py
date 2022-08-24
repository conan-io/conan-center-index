from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class PatchElfConan(ConanFile):
    name = "patchelf"
    description = "A small utility to modify the dynamic linker and RPATH of ELF executables"
    topics = ("conan", "elf", "linker", "interpreter", "RPATH", "binaries")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NixOS/patchelf"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    def validate(self):
        if not tools.apple.is_apple_os(self) and self.settings.os not in ("FreeBSD", "Linux"):
            raise ConanInvalidConfiguration("PatchELF is only available for GNU-like operating systems (e.g. Linux)")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure(configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        with tools.files.chdir(self, self._source_subfolder):
            self.run("{} -fiv --warnings=all".format(tools.get_env("AUTORECONF")), run_environment=True)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
