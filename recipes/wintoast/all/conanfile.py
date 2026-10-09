import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file

required_conan_version = ">=2.4"


class WinToastConan(ConanFile):
    name = "wintoast"
    description = "Lightweight library which brings a complete integration of the modern toast notifications of Windows"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mohabouje/WinToast"
    topics = ("windows", "toast", "notification")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration(f"WinToast is only supported on Windows")
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD ",
                        "#")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["WINTOASTLIB_BUILD_EXAMPLES"] = False
        tc.cache_variables["WINTOASTLIB_QT_ENABLED"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "WinToast")
        self.cpp_info.set_property("cmake_target_name", "WinToast::WinToast")
        self.cpp_info.libs = ["WinToast"]
        self.cpp_info.system_libs = ["psapi"]
