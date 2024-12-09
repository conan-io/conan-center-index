import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, save

required_conan_version = ">=1.53.0"

class LibE57FormatConan(ConanFile):
    name = "libe57format"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/asmaloney/libE57Format"
    description = "Library for reading & writing the E57 file format"
    topics = ("e57", "io", "point-cloud")

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

    def requirements(self):
        self.requires("xerces-c/3.2.5")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "11")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16.3 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()
        tc = CMakeToolchain(self)
        tc.variables["E57_BUILD_SHARED"] = self.options.shared
        tc.variables["E57_BUILD_TEST"] = False
        tc.variables["USING_STATIC_XERCES"] = not self.dependencies["xerces-c"].options.shared
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "e57format")
        self.cpp_info.set_property("cmake_target_name", "E57Format")
        suffix = "-d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"E57Format{suffix}"]
        if self.settings.os in ["Linux", "FreeBSD"] and not self.options.shared:
            self.cpp_info.system_libs.extend(["m", "pthread"])
