from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import load, get, apply_conandata_patches, rmdir, copy
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
import os

class NanodbcConan(ConanFile):
    name = "nanodbc"
    description = "A small C++ wrapper for the native C ODBC API"
    topics = ("conan", "nanodbc", "odbc", "database")
    license = "MIT"
    homepage = "https://github.com/nanodbc/nanodbc/"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "async": [True, False],
        "unicode": [True, False],
        "with_boost": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "async": True,
        "unicode": False,
        "with_boost": False,
    }

    generators = "CMakeDeps"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        check_min_cppstd(self, 14)

    def requirements(self):
        if self.options.with_boost:
            self.requires("boost/1.76.0")
        if self.settings.os != "Windows":
            self.requires("odbc/2.3.9")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        tc.cache_variables["NANODBC_DISABLE_ASYNC"] = not self.options.get_safe("async")
        tc.cache_variables["NANODBC_ENABLE_UNICODE"] = self.options.unicode
        tc.cache_variables["NANODBC_ENABLE_BOOST"] = self.options.with_boost
        tc.cache_variables["NANODBC_DISABLE_LIBCXX"] = self.settings.get_safe("compiler.libcxx") != "libc++"

        tc.cache_variables["NANODBC_DISABLE_INSTALL"] = False
        tc.cache_variables["NANODBC_DISABLE_EXAMPLES"] = True
        tc.cache_variables["NANODBC_DISABLE_TESTS"] = True

        tc.generate()

    def build(self):
        apply_conandata_patches(self)

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

        if not self.options.shared and self.settings.os == "Windows":
            self.cpp_info.system_libs = ["odbc32"]
