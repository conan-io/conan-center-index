from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.scm import Version
from conan.errors import ConanException
import os

required_conan_version = ">=1.50.0"


class AdeConan(ConanFile):
    name = "ade"
    license = "Apache-2.0"
    homepage = "https://github.com/opencv/ade"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Graph construction, manipulation, and processing framework"
    topics = ("graphs", "opencv")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        if Version(self.version) > "0.1.2d": # pylint: disable=conan-unreachable-upper-version
            raise ConanException("CMAKE_POLICY_VERSION_MINIMUM hardcoded to 3.5, check if new version supports CMake 4")
        tc.generate()

    def build(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "    if(UNIX)", "    if(UNIX OR CYGWIN OR MINGW OR MSYS)")
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ade")
        self.cpp_info.set_property("cmake_target_name", "ade")
        self.cpp_info.libs = ["ade"]
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            self.cpp_info.system_libs.append("ssp")
