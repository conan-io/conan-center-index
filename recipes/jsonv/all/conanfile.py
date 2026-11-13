from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class JsonvConan(ConanFile):
    name = "jsonv"
    description = "A modern C++ library for interacting with JSON."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tgockel/json-voorhees"
    topics = ("json", "json-serialization")
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

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "13",
            "clang": "19",
            "apple-clang": "16",
            "msvc": "195",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 23)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires {self.settings.compiler} {minimum_version} or newer"
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.23 <5]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["JSONV_BUILD_TESTS"] = False
        tc.cache_variables["JSONV_BUILD_BENCHMARK"] = False
        tc.cache_variables["JSONV_BUILD_FUZZERS"] = False
        tc.cache_variables["JSONV_INSTALL"] = True
        # A static library of LTO bitcode cannot be linked by a consumer built without LTO.
        tc.cache_variables["JSONV_LTO"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "build"))
        rm(self, "*.pdb", self.package_folder, recursive=True)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "jsonv")
        self.cpp_info.set_property("cmake_target_name", "jsonv::jsonv")
        self.cpp_info.set_property("pkg_config_name", "libjsonv")
        self.cpp_info.libs = ["jsonv"]
        if not self.options.shared:
            # config.hpp defaults to JSONV_SO=1, which on MSVC declares the API __declspec(dllimport).
            self.cpp_info.defines = ["JSONV_SO=0"]
