from conan import ConanFile
from conan.tools.files import get, copy, rmdir, collect_libs
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"


class ChaiScriptConan(ConanFile):
    name = "chaiscript"
    homepage = "https://github.com/ChaiScript/ChaiScript"
    description = "Embedded Scripting Language Designed for C++."
    topics = ("conan", "embedded-scripting-language", "language")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False], "dyn_load": [True, False], "use_std_make_shared": [True, False],
               "multithread_support": [True, False],
               "header_only": [True, False]}
    default_options = {"fPIC": True, "dyn_load": True,
                       "use_std_make_shared": True,
                       "multithread_support": True,
                       "header_only": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # BUILD_SHARED_LIBS and POSITION_INDEPENDENT_CODE are automatically parsed when self.options.shared or self.options.fPIC exist
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_SAMPLES"] = False
        tc.variables["BUILD_MODULES"] = True
        tc.variables["USE_STD_MAKE_SHARED"] = self.options.use_std_make_shared
        tc.variables["DYNLOAD_ENABLED"] = self.options.dyn_load
        tc.variables["MULTITHREAD_SUPPORT_ENABLED"] = self.options.multithread_support
        tc.generate()

    def build(self):
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.options.header_only:
            copy(self, pattern="*.hpp",
                dst=os.path.join(self.package_folder, "include"),
                src=os.path.join(self.source_folder, "include"))
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def package_info(self):
        if not self.options.header_only:
            self.cpp_info.libs = collect_libs(self)
        if self.options.use_std_make_shared:
            self.cpp_info.defines.append("CHAISCRIPT_USE_STD_MAKE_SHARED")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("dl")
            if self.options.multithread_support:
                self.cpp_info.system_libs.append("pthread")
