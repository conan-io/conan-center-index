import os
import sys
import textwrap
import time

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, load, save
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, VCVars
from conan.tools.scm import Version

required_conan_version = ">=1.47.0"


class GnConan(ConanFile):
    name = "gn"
    description = "GN is a meta-build system that generates build files for Ninja."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gn.googlesource.com/"
    topics = ("build system", "ninja")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    @property
    def _minimum_compiler_version_supporting_cxx17(self):
        return {
            "Visual Studio": 15,
            "msvc": 191,
            "gcc": 7,
            "clang": 4,
            "apple-clang": 10,
        }.get(str(self.settings.compiler))

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 17)
        else:
            if self._minimum_compiler_version_supporting_cxx17:
                if Version(self.settings.compiler.version) < self._minimum_compiler_version_supporting_cxx17:
                    raise ConanInvalidConfiguration("gn requires a compiler supporting c++17")
            else:
                self.output.warning(
                    "gn recipe does not recognize the compiler. gn requires a compiler supporting c++17."
                    " Assuming it does."
                )

    def build_requirements(self):
        # FIXME: add cpython build requirements for `build/gen.py`.
        self.build_requires("ninja/1.11.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version])

    @property
    def _gn_platform(self):
        if is_apple_os(self):
            return "darwin"
        if is_msvc(self):
            return "msvc"
        # Assume gn knows about the os
        return str(self.settings.os).lower()

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if is_msvc(self):
            vcvars = VCVars(self)
            vcvars.generate()

        configure_args = [
            "--no-last-commit-position",
            f"--host={self._gn_platform}",
        ]
        if self.settings.build_type in ["Debug", "RelWithDebInfo"]:
            configure_args.append("-d")
        save(self, os.path.join(self.source_folder, "configure_args"), " ".join(configure_args))

    def build(self):
        with chdir(self, self.source_folder):
            # Generate dummy header to be able to run `build/ben.py` with `--no-last-commit-position`. This allows running the script without the tree having to be a git checkout.
            save(
                self,
                os.path.join("src", "gn", "last_commit_position.h"),
                textwrap.dedent("""\
                    #pragma once
                    #define LAST_COMMIT_POSITION "1"
                    #define LAST_COMMIT_POSITION_NUM 1
                    """),
            )
            self.run(f"{sys.executable} build/gen.py " + load(self, "configure_args"))
            # Try sleeping one second to avoid time skew of the generated ninja.build file (and having to re-run build/gen.py)
            time.sleep(1)
            build_args = ["-C", "out", f"-j{os.cpu_count()}"]
            self.run("ninja " + " ".join(build_args))

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if self.settings.os == "Windows":
            copy(self,
                 "gn.exe",
                 src=os.path.join(self.source_folder, "out"),
                 dst=os.path.join(self.package_folder, "bin"))
        else:
            copy(self, "gn",
                 src=os.path.join(self.source_folder, "out"),
                 dst=os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
