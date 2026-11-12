from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class NanodbcConan(ConanFile):
    name = "nanodbc"
    description = "A small C++ wrapper for the native C ODBC API"
    topics = ("odbc", "database")
    license = "MIT"
    homepage = "https://github.com/nanodbc/nanodbc/"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "async": [True, False],
        "unicode": [True, False],
        "with_boost": [True, False],
        "utf8": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "async": True,
        "unicode": False,
        "with_boost": False,
        "utf8": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "3.0.0":
            self.options.rm_safe("utf8")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21]")

    def requirements(self):
        if self.options.with_boost:
            self.requires("boost/1.83.0")
        if self.settings.os != "Windows":
            self.requires("odbc/2.3.11")

    def validate(self):
        check_min_cppstd(self, 17 if Version(self.version) >= "3.0.0" else 14)
        if self.options.with_boost and not self.options.unicode:
            raise ConanInvalidConfiguration("with_boost option requires unicode option to be enabled. See https://github.com/nanodbc/nanodbc#build-options")
        if self.options.unicode and self.options.get_safe("utf8"):
            # https://github.com/nanodbc/nanodbc/blob/v3.0.8/CMakeLists.txt#L164
            raise ConanInvalidConfiguration("unicode and utf8 options are alternatives; enable only one")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["NANODBC_DISABLE_ASYNC"] = not self.options.get_safe("async")
        tc.cache_variables["NANODBC_ENABLE_UNICODE"] = self.options.unicode
        tc.cache_variables["NANODBC_ENABLE_BOOST"] = self.options.with_boost
        tc.cache_variables["NANODBC_FORCE_LIBCXX"] = self.settings.get_safe("compiler.libcxx") == "libc++"
        tc.cache_variables["NANODBC_GENERATE_INSTALL"] = True
        tc.cache_variables["NANODBC_BUILD_EXAMPLES"] = False
        tc.cache_variables["NANODBC_BUILD_TESTS"] = False
        if Version(self.version) >= "3.0.0":
            tc.cache_variables["NANODBC_ENABLE_UTF8"] = self.options.utf8

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["nanodbc"]
        if self.options.unicode:
            self.cpp_info.defines.append("NANODBC_ENABLE_UNICODE")
            if is_msvc(self):
                self.cpp_info.defines.extend(["_UNICODE", "UNICODE"])
        if self.options.with_boost:
            self.cpp_info.defines.append("NANODBC_ENABLE_BOOST")
        if not self.options.get_safe("async"):
            self.cpp_info.defines.append("NANODBC_DISABLE_ASYNC")
        if self.options.get_safe("utf8"):
            self.cpp_info.defines.append("NANODBC_ENABLE_UTF8")

        if not self.options.shared and self.settings.os == "Windows":
            self.cpp_info.system_libs = ["odbc32"]
