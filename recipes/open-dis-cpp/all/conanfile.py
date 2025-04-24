import os

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version

required_conan_version = ">=2.1"


class OpenDisConan(ConanFile):
    name = "open-dis-cpp"
    homepage = "https://open-dis.org"
    description = "C++ implementation of the IEEE-1278.1 Distributed Interactive Simulation (DIS) application protocol v6 and v7"
    topics = ("library","protocol","simulation-framework","dis")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-2-Clause"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_EXAMPLES"] = "FALSE"
        tc.cache_variables["BUILD_TESTS"] = "FALSE"
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        if Version(self.version) > "1.1.0": # pylint: disable=conan-unreachable-upper-version
            raise ConanException("CMAKE_POLICY_VERSION_MINIMUM hardcoded to 3.5, check if new version supports CMake 4")
        tc.generate()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.info.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "res"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "OpenDIS")
        self.cpp_info.set_property("cmake_file_name", "OpenDIS")

        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["OpenDIS6"].libs = ["OpenDIS6"]
        self.cpp_info.components["OpenDIS7"].libs = ["OpenDIS7"]

        self.cpp_info.components["OpenDIS6"].set_property("cmake_target_name", "OpenDIS::OpenDIS6")
        self.cpp_info.components["OpenDIS6"].set_property("cmake_target_aliases", ["OpenDIS::DIS6","OpenDIS6"])
        self.cpp_info.components["OpenDIS7"].set_property("cmake_target_name", "OpenDIS::OpenDIS7")
        self.cpp_info.components["OpenDIS7"].set_property("cmake_target_aliases", ["OpenDIS::DIS7","OpenDIS7"])
