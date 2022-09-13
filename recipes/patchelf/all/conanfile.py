from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, rmdir, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.env import VirtualBuildEnv
import os

required_conan_version = ">=1.51.3"

class PatchElfConan(ConanFile):
    name = "patchelf"
    description = "A small utility to modify the dynamic linker and RPATH of ELF executables"
    topics = ("conan", "elf", "linker", "interpreter", "RPATH", "binaries")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NixOS/patchelf"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "8",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def build_requirements(self):
        self.tool_requires("libtool/2.4.6")

    def validate(self):
        if not is_apple_os(self) and self.info.settings.os not in ("FreeBSD", "Linux"):
            raise ConanInvalidConfiguration("PatchELF is only available for GNU-like operating systems (e.g. Linux)")

        if Version(self.version) >= "0.15":
            if self.info.settings.get_safe("compiler.cppstd"):
                check_min_cppstd(self, self._minimum_cpp_standard)
            minimum_version = self._compilers_minimum_version.get(str(self.info.settings.get_safe("compiler")), False)
            if minimum_version and Version(self.info.settings.get_safe("compiler.version")) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
        self.buildenv_info.append("PATH", bin_path)
        self.runenv_info.define("PATH", bin_path)

        self.cpp_info.libdirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []
