from conan import ConanFile
from conan.tools.files import get, copy, collect_libs
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"


class CargsConan(ConanFile):
    name = "cargs"
    description = "A lightweight getopt replacement that works on Linux, " \
                  "Windows and macOS. Command line argument parser library" \
                  " for C/C++. Can be used to parse argv and argc parameters."
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "https://likle.github.io/cargs/"
    topics = ("cargs", "cross-platform", "windows", "macos", "osx", "linux",
              "getopt", "getopt-long", "command-line-parser", "command-line",
              "arguments", "argument-parser")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared and self.settings.os == "Windows"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="cargs")

    def package(self):
        copy(self, pattern="LICENSE.md", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="cargs.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
        copy(self, pattern="*.a", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, pattern="*.dylib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, pattern="*.so*", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        copy(self, pattern="*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
