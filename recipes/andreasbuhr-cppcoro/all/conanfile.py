import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class AndreasbuhrCppCoroConan(ConanFile):
    name = "andreasbuhr-cppcoro"
    description = "A library of C++ coroutine abstractions for the coroutines TS"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/andreasbuhr/cppcoro"
    topics = ("cpp", "async", "coroutines")

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
    provides = "cppcoro"

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "10",
            "clang": "8",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        # We can't simply check for C++20, because clang and MSVC support the coroutine TS despite not having labeled (__cplusplus macro) C++20 support
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if min_version and Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(
                f"{self.name} requires coroutine TS support. The current compiler"
                f" {self.settings.compiler} {self.settings.compiler.version} does not support it."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cppcoro")
        self.cpp_info.set_property("cmake_target_name", "cppcoro::cppcoro")

        self.cpp_info.libs = ["cppcoro"]

        if self.settings.os in ["Linux", "FreeBSD"] and self.options.shared:
            self.cpp_info.system_libs = ["pthread", "m"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["synchronization", "mswsock", "ws2_32"]

        if is_msvc(self):
            self.cpp_info.cxxflags.append("/await")
        elif self.settings.compiler == "gcc":
            self.cpp_info.cxxflags.append("-fcoroutines")
            self.cpp_info.defines.append("CPPCORO_COMPILER_SUPPORTS_SYMMETRIC_TRANSFER=1")
        elif ((self.settings.compiler == "clang" and Version(self.settings.compiler.version).major < 17) or
              self.settings.compiler == "apple-clang"): # apple-clang has not released a version with LLVM 17+ yet
            self.cpp_info.cxxflags.append("-fcoroutines-ts")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "cppcoro"
        self.cpp_info.filenames["cmake_find_package_multi"] = "cppcoro"
        self.cpp_info.names["cmake_find_package"] = "cppcoro"
        self.cpp_info.names["cmake_find_package_multi"] = "cppcoro"
