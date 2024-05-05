from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building, check_min_cppstd
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

import os

required_conan_version = ">=1.54.0"

class PatchElfConan(ConanFile):
    name = "patchelf"
    package_type = "application"
    description = "A small utility to modify the dynamic linker and RPATH of ELF executables"
    topics = ("conan", "elf", "linker", "interpreter", "RPATH", "binaries")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NixOS/patchelf"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return "11" if Version(self.version) < "0.18" else "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "17": {
                # patchelf/0.18.0 requires gcc >= 8
                "gcc": "8",
                "clang": "5",
                "apple-clang": "10",
                "Visual Studio": "15",
                "msvc": "191",
            },
        }.get(self._min_cppstd, {})

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.6")

    def validate(self):
        if not is_apple_os(self) and self.settings.os not in ("FreeBSD", "Linux"):
            raise ConanInvalidConfiguration(f"{self.ref} is only available for GNU-like operating systems (e.g. Linux)")

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.generate()

        tc = AutotoolsDeps(self)
        tc.generate()

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

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
