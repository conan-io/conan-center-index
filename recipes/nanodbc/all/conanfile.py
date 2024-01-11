from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


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
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "async": True,
        "unicode": False,
        "with_boost": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "3.4",
            "Visual Studio": "14",
            "msvc": "190",
            "apple-clang": "9.1",  # FIXME: this is a guess
        }

    def requirements(self):
        if self.options.with_boost:
            self.requires("boost/1.83.0")
        if self.settings.os != "Windows":
            self.requires("odbc/2.3.11")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 14)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

        if self.settings.compiler == "apple-clang" and Version(self.version) < "2.14.0":
            raise ConanInvalidConfiguration("""
                `apple-clang` compilation is supported only for version 2.14.0 and up.
                See https://github.com/nanodbc/nanodbc/issues/274 for more details.
                """)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["NANODBC_DISABLE_ASYNC"] = not self.options.get_safe("async")
        tc.cache_variables["NANODBC_ENABLE_UNICODE"] = self.options.unicode
        tc.cache_variables["NANODBC_ENABLE_BOOST"] = self.options.with_boost
        tc.cache_variables["NANODBC_DISABLE_LIBCXX"] = self.settings.get_safe("compiler.libcxx") != "libc++"
        tc.cache_variables["NANODBC_DISABLE_INSTALL"] = False
        tc.cache_variables["NANODBC_DISABLE_EXAMPLES"] = True
        tc.cache_variables["NANODBC_DISABLE_TESTS"] = True
        tc.cache_variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # No warnings as errors
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "-Werror", "")

    def build(self):
        self._patch_sources()
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
        self.cpp_info.set_property("cmake_file_name", "nanodbc")
        self.cpp_info.set_property("cmake_target_name", "nanodbc::nanodbc")
        self.cpp_info.libs = ["nanodbc"]

        if not self.options.shared and self.settings.os == "Windows":
            self.cpp_info.system_libs = ["odbc32"]
