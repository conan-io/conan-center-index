import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rename, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "nanobind"
    description = "Tiny and efficient C++/Python bindings"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/wjakob/nanobind"
    topics = ("python", "bindings", "pybind11", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
            "msvc": "192",
            "Visual Studio": "15",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        self.requires("tsl-robin-map/1.3.0")

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
        tc.variables["NB_TEST"] = False
        tc.variables["NB_USE_SUBMODULE_DEPS"] = False
        tc.generate()

    def _patch_sources(self):
        # Look for headers in <package_folder>/include
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "nanobind-config.cmake"),
                        "${NB_DIR}/include",
                        "${NB_DIR}/../../include")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _cmake_rel_dir(self):
        return os.path.join("lib", "nanobind", "cmake")

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rename(self,
               os.path.join(self.package_folder, "share"),
               os.path.join(self.package_folder, "lib"))
        rename(self,
               os.path.join(self.package_folder, "lib", "nanobind", "include"),
               os.path.join(self.package_folder, "include"))
        rename(self,
               os.path.join(self.package_folder, self._cmake_rel_dir, "nanobind-config.cmake"),
               os.path.join(self.package_folder, self._cmake_rel_dir, "nanobind.cmake"))

    def package_info(self):
        self.cpp_info.builddirs = [self._cmake_rel_dir]
        self.cpp_info.set_property("cmake_build_modules", [os.path.join(self._cmake_rel_dir, "nanobind.cmake")])
