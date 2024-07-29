import os
import sys

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout


required_conan_version = ">=1.53.0"

class HermesConan(ConanFile):
    name = "hermes"
    description = "A JavaScript engine optimized for running React Native."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facebook/hermes"
    topics = ("javascript", "ahead-of-time", "react native")
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    short_paths = True

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("icu/74.2")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def validate_build(self):
        if getattr(sys, "frozen", False):
            raise ConanInvalidConfiguration("This package cannot be built with a Conan self-contained executable, "
                                            "needs full Python installation")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["HERMES_USE_STATIC_ICU"] = not self.dependencies["icu"].options.shared
        tc.cache_variables["HERMES_ENABLE_TEST_SUITE"] = False
        tc.cache_variables["HERMES_IS_ANDROID"] = self.settings.os == "Android"
        tc.cache_variables["HERMES_ENABLE_WIN10_ICU_FALLBACK"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        venv = VirtualBuildEnv(self)
        venv.generate(scope="build")

    def build(self):
        if self.settings.os == "Windows":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "target_link_libraries(${target_name} dl pthread)", "")
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["hermes"]
