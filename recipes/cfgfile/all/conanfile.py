from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class CfgfileConan(ConanFile):
    name = "cfgfile"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/igormironchik/cfgfile.git"
    license = "MIT"
    description = "Header-only library for reading/saving configuration files with schema defined in sources."
    topics = ("configuration", "file")
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "5",
            "clang": "3.5",
            "apple-clang": "10",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.version == "0.2.9.1" or Version(self.version) >= "0.2.10":
            self.requires("args-parser/6.2.0.1")
        elif self.version == "0.2.9.0":
            self.requires("args-parser/6.0.1.0")

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.19 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_TESTS"] = False
        if Version(self.version) >= "0.2.9":
            tc.variables["USE_INTERNAL_ARGS_PARSER"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_folder)
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cfgfile")
        self.cpp_info.set_property("cmake_target_name", "cfgfile::cfgfile")
        self.cpp_info.includedirs.append(os.path.join("include", "cfgfile"))

        # TODO: to remove once conan v1 support dropped
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
