import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class KittenConan(ConanFile):
    name = "kitten"
    description = "A small C++ library inspired by Category Theory focused on functional composition."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rvarago/kitten"
    topics = ("category-theory", "composition", "monadic-interface", "declarative-programming", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "7",
            "clang": "5",
            "Visual Studio": "15.7",
            "apple-clang": "10",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if min_version and Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(f"{self.name} requires C++{self._min_cppstd}, which your compiler does not support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "kitten")
        self.cpp_info.set_property("cmake_target_name", "rvarago::kitten")
        self.cpp_info.components["libkitten"].set_property("cmake_target_name", "rvarago::kitten")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "kitten"
        self.cpp_info.filenames["cmake_find_package_multi"] = "kitten"
        self.cpp_info.names["cmake_find_package"] = "rvarago"
        self.cpp_info.names["cmake_find_package_multi"] = "rvarago"
        self.cpp_info.components["libkitten"].names["cmake_find_package"] = "kitten"
        self.cpp_info.components["libkitten"].names["cmake_find_package_multi"] = "kitten"
