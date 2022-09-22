from conan import ConanFile
from conan.tools.files import save

from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.files import apply_conandata_patches, copy, get, patch, rmdir
from conan.tools import build

import os
import textwrap

required_conan_version = ">=1.52.0"

class CppfrontConan(ConanFile):
    name = "cppfront"
    description = "Cppfront is a experimental compiler from a potential C++ 'syntax 2' (Cpp2) to today's 'syntax 1' (Cpp1)"
    topics = ("cppfront", "cpp2")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hsutter/cppfront"
    license = "CC-BY-NC-ND-4.0"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _compilers_minimum_version(self):
        return {"gcc": "11",
                "Visual Studio": "16.9",
                "clang": "13",
                "apple-clang": "13",
                }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    # def generate(self):
    #     tc = CMakeToolchain(self)
    #     # tc.variables["BUILD_TESTING"] = False
    #     tc.generate()

    # def validate(self):
    #     if self.info.settings.compiler.cppstd:
    #         check_min_cppstd(self, "20")

    #     minimum_version = self._compilers_minimum_version.get(str(self.info.settings.compiler), False)
    #     compiler_version = Version(self.info.settings.compiler.version)
    #     if minimum_version and Version(self.info.settings.compiler.version) < minimum_version:
    #         raise ConanInvalidConfiguration(
    #             "{} requires C++17, which your compiler does not support.".format(self.name)
    #         )

    #     if self.info.settings.compiler == "clang" and (compiler_version >= "10" and compiler_version < "12"):
    #         raise ConanInvalidConfiguration(
    #             "AA+ cannot handle clang 10 and 11 due to filesystem being under experimental namespace"
    #         )

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, "20")

        # if self.settings.compiler == "Visual Studio":
        #     raise ConanInvalidConfiguration("CppFront does not support MSVC yet (https://github.com/jfalcou/eve/issues/1022).")
        # if self.settings.compiler == "apple-clang":
        #     raise ConanInvalidConfiguration("CppFront does not support apple Clang due to an incomplete libcpp.")

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{} {} requires C++20. Your compiler is unknown. Assuming it supports C++20.".format(self.name, self.version))
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("{} {} requires C++20, which your compiler does not support.".format(self.name, self.version))



    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()


    def build(self):
        # apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "bin", "test cases"))

        cmake = CMake(self)
        cmake.install()

        # # create wrapper scripts
        # save(self, os.path.join(self.package_folder, "bin", "meson.cmd"), textwrap.dedent("""\
        #     @echo off
        #     CALL python %~dp0/meson.py %*
        # """))
        # save(self, os.path.join(self.package_folder, "bin", "meson"), textwrap.dedent("""\
        #     #!/usr/bin/env bash
        #     meson_dir=$(dirname "$0")
        #     exec "$meson_dir/meson.py" "$@"
        # """))

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)

        # self._chmod_plus_x(os.path.join(bin_path, "cppfront"))
        # self.cpp_info.builddirs = [os.path.join("bin", "cppfrontbuild", "cmake", "data")]

        bin_ext = ".exe" if self.settings.os == "Windows" else ""
        cppfront_bin = os.path.join(self.package_folder, "bin", "cppfront{}".format(bin_ext)).replace("\\", "/")

        # M4 environment variable is used by a lot of scripts as a way to override a hard-coded embedded m4 path
        self.output.info("Setting M4 environment variable: {}".format(cppfront_bin))
        self.env_info.cppfront = cppfront_bin

        self.cpp_info.frameworkdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

