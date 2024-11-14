import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, rm, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"

class libqConan(ConanFile):
    name = "libq"
    description = "A platform-independent promise library for C++, implementing asynchronous continuations."
    license = "Apache-2.0"
    topics = ("async", "promises")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/grantila/q"
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = {
        "shared": [True, False]
    }
    default_options = {
        "shared": False
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "7"
        }

    @property
    def _build_tests(self):
        return not self.conf.get("tools.build:skip_test", default=True, check_type=bool)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self._build_tests:
            self.test_requires("gtest/1.14.0")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if self.settings.os in ["Windows"]:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built on Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["q_BUILD_TESTS"] = self._build_tests
        tc.variables["q_BUILD_APPS"] = False

        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'include_directories( "3rdparty/gtest-1.8.0/include/" )',
                        "")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'add_subdirectory( "3rdparty/gtest-1.8.0" )',
                        "find_package(GTest REQUIRED)\n")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.set_property("cmake_file_name", "libq")
        self.cpp_info.set_property("cmake_target_name", "libq::libq")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")
