from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file

import os

required_conan_version = ">=2.1"


class SbgEComConan(ConanFile):
    name = "sbgecom"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/SBG-Systems/sbgECom"
    description = "C library used to communicate with SBG Systems IMU, AHRS and INS"
    topics = ("sbg", "imu", "ahrs", "ins")
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    implements = ["auto_shared_fpic"]
    languages = "C"
    
    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_POSITION_INDEPENDENT_CODE",
                        "# set(CMAKE_POSITION_INDEPENDENT_CODE")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["sbgECom"]
        self.cpp_info.set_property("cmake_file_name", "sbgECom")
        self.cpp_info.set_property("cmake_target_name", "sbgECom::sbgECom")
        self.cpp_info.defines = ["SBG_COMMON_STATIC_USE"]
        if self.settings.compiler == "msvc":
            self.cpp_info.system_libs = ["ws2_32"]
