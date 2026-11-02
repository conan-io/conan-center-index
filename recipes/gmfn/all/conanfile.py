import os

from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.build import check_max_cppstd, check_min_cppstd

required_conan_version = ">=2.30"


class GMFNConan(ConanFile):
    name = "gmfn"
    description = "GMFN is a small C++23 library that provides exception-free wrappers around the WinAPI for retrieving the file path of a loaded Windows module."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/NsPro04/GetModuleFileName"
    topics = ("cpp", "cpp23", "library", "win32", "winapi", "windows")

    languages = "C++"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": False
    }

    def build_requirements(self):
        self.tool_requires("cmake/[>=4.3.1]")

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("GMFN is only supported on Windows")
        check_min_cppstd(self, 23)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "GMFN")
        self.cpp_info.set_property("cmake_target_name", "GMFN::GMFN")
        self.cpp_info.libs = ["GMFN"]

        if self.options.shared:
            self.cpp_info.defines.append("GMFN_NO_AUTO_LINK")
        else:
            self.cpp_info.defines.append("GMFN_STATIC_LIB")