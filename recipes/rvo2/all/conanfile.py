import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file

required_conan_version = ">=1.53.0"


class Rvo2Conan(ConanFile):
    name = "rvo2"
    description = "Optimal Reciprocal Collision Avoidance"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/snape/RVO2"
    topics = ("collision", "avoidance")

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "add_subdirectory(examples)", "")
        replace_in_file(
            self,
            os.path.join(self.source_folder, "src", "CMakeLists.txt"),
            "DESTINATION include",
            "DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}",
        )
        replace_in_file(
            self,
            os.path.join(self.source_folder, "src", "CMakeLists.txt"),
            "RVO DESTINATION lib",
            "RVO RUNTIME LIBRARY ARCHIVE",
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["RVO"]
