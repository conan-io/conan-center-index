from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file
from conan.tools.scm import Version
import os


required_conan_version = ">=2"

class PackageConan(ConanFile):
    name = "ctd_cli"
    description = "Modern C++20 Command Line Interface with strongly typed arguments."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.com/slavic-demons/korgorusze/compile_time_defined_cli"
    topics = ("command line arguments", "command line interface", "embedded")
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
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate_build(self):
        if self.settings.compiler == "msvc" and self.options.shared:
            raise ConanInvalidConfiguration("The library does not support shared builds with MSVC")

    def validate(self):
        check_min_cppstd(self, 20)
        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "14":
            raise ConanInvalidConfiguration("The library requires std::range support, which is not available in apple-clang < 14")

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "12":
            raise ConanInvalidConfiguration("The library requires constexpr std::vector support, which is not available in gcc < 12")

        if self.settings.compiler == "msvc" and Version(self.settings.compiler.version) < "193":
            raise ConanInvalidConfiguration("The library requires MSVC >= 193")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD 20)", "")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20]")

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
        self.cpp_info.libs = ["ctd_cli"]
        self.cpp_info.set_property("cmake_file_name", "ctd_cli")
        self.cpp_info.set_property("cmake_target_name", "korgorusze::CLI")
