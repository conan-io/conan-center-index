import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"

class LagerConan(ConanFile):
    name = "lager"
    description = "C++ library for value-oriented design using the unidirectional data-flow architecture"
    license = "MIT"
    homepage = "https://sinusoid.es/lager/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("redux", "functional-programming", "interactive", "value-semantics", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "clang": "10",
            "apple-clang": "11",
            "msvc": "192",
            "Visual Studio": "16.2",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.83.0")
        self.requires("zug/0.1.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)


    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["lager_BUILD_EXAMPLES"] = False
        tc.cache_variables["lager_BUILD_TESTS"] = False
        tc.cache_variables["lager_BUILD_DOCS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        # Do not inject the package folder path into the library.
        # This is only used for examples.
        replace_in_file(self, os.path.join(self.source_folder, "lager", "resources_path.hpp.in"),
                        '"@LAGER_PREFIX_PATH@"', "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

