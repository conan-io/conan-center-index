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

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, "20")

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
        copy(self, "cppfront*", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))
        copy(self, pattern="*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "bin", "test cases"))

        cmake = CMake(self)
        cmake.install()

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package_info(self):
        # bin_path = os.path.join(self.package_folder, "bin")
        # self.output.info(f"Appending PATH environment variable: {bin_path}")
        # self.env_info.PATH.append(bin_path)

        bin_ext = ".exe" if self.settings.os == "Windows" else ""
        cppfront_bin = os.path.join(self.package_folder, "bin", "cppfront{}".format(bin_ext)).replace("\\", "/")

        # CppFront environment variable is used by a lot of scripts as a way to override a hard-coded embedded m4 path
        self.output.info("Setting CppFront environment variable: {}".format(cppfront_bin))
        self.env_info.cppfront = cppfront_bin

        self.cpp_info.frameworkdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # target = "cppfront"
        # self.cpp_info.set_property("cmake_file_name", "cppfront")
        # self.cpp_info.set_property("cmake_target_name", f"cppfront::{target}")
        # self.cpp_info.set_property("pkg_config_name",  "cppfront")

        # # TODO: to remove in conan v2 once cmake_find_package* generators removed
        # self.cpp_info.names["cmake_find_package"] = "cppfront"
        # self.cpp_info.names["cmake_find_package_multi"] = "cppfront"
        # self.cpp_info.names["pkg_config"] = "cppfront"
        # self.cpp_info.components["_cppfront"].names["cmake_find_package"] = target
        # self.cpp_info.components["_cppfront"].names["cmake_find_package_multi"] = target
        # self.cpp_info.components["_cppfront"].set_property("cmake_target_name", f"cppfront::{target}")

