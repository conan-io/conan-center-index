from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get, rmdir, copy
from conan.tools.microsoft import is_msvc, check_min_vs
from conan.tools.build import check_min_cppstd
from conan import Version
from conan.errors import ConanInvalidConfiguration
import os


class ChaiScriptConan(ConanFile):
    name = "chaiscript"
    homepage = "https://github.com/ChaiScript/ChaiScript"
    description = "Embedded Scripting Language Designed for C++."
    topics = ("embedded-scripting-language", "language")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    settings = "os", "compiler", "build_type", "arch"
    package_type = "shared-library"
    options = {"fPIC": [True, False],
               "dyn_load": [True, False],
               "use_std_make_shared": [True, False],
               "multithread_support": [True, False],
               "header_only": [True, False]}
    default_options = {"fPIC": True,
                       "dyn_load": True,
                       "use_std_make_shared": True,
                       "multithread_support": True,
                       "header_only": True}

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only:
            self.package_type = "header-library"
            self.options.rm_safe("fPIC")
            del self.options.dyn_load
            del self.options.use_std_make_shared
            del self.options.multithread_support

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_SAMPLES"] = False
        tc.variables["BUILD_MODULES"] = True
        tc.variables["USE_STD_MAKE_SHARED"] = self.options.get_safe("use_std_make_shared")
        tc.variables["DYNLOAD_ENABLED"] = self.options.get_safe("dyn_load")
        tc.variables["MULTITHREAD_SUPPORT_ENABLED"] = self.options.get_safe("multithread_support")
        tc.generate()

    def build(self):
        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.options.header_only:
            copy(self, pattern="*.hpp", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, 'include'))
        else:
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        if not self.options.header_only:
            self.cpp_info.libdirs = ["lib", os.path.join("lib", "chaiscript")]
            # INFO: chaiscript provides module libraries, can not be linked directly
            self.cpp_info.libs = []
        if self.options.get_safe("use_std_make_shared"):
            self.cpp_info.defines.append("CHAISCRIPT_USE_STD_MAKE_SHARED")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["dl"]
            if self.options.get_safe("multithread_support") or self.options.header_only:
                self.cpp_info.system_libs.append("pthread")
