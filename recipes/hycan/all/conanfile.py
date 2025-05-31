import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import copy, get, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class HyCANConan(ConanFile):
    name = "hycan"
    description = "Modern high-performance Linux C++ CAN communication protocol library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/RoboMaster-DLMU-CONE/HyCAN"
    topics = ("can", "canbus", "linux", "network")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "clang": "13",
        }

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                f"{self.ref} is a Linux-only library. {self.settings.os} is not supported."
            )

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler)
        )
        if (
            minimum_version
            and Version(self.settings.compiler.version) < minimum_version
        ):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd} support. "
                f"The current compiler {self.settings.compiler} {self.settings.compiler.version} does not support it."
            )

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("xtr/2.1.2", transitive_headers=True)
        self.requires("libnl/3.9.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_HYCAN_EXAMPLE"] = False
        tc.cache_variables["BUILD_HYCAN_TEST"] = False
        tc.cache_variables["TEST_HYCAN_LATENCY"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["hycan"]
        self.cpp_info.system_libs = ["pthread"]
