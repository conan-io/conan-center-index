import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class SiConan(ConanFile):
    name = "si"
    description = (
        "A header only c++ library that provides type safety and user defined literals "
        "for handling physical values defined in the International System of Units."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bernedom/SI"
    topics = ("physical units", "SI-unit-conversion", "cplusplus-library", "cplusplus-17", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15",
            "clang": "5",
            "apple-clang": "10",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    "'si' requires C++17, which your compiler "
                    f"({self.settings.compiler} {self.settings.compiler.version}) does not support.")
        else:
            self.output.warning("'si' requires C++17. Your compiler is unknown. Assuming it supports C++17.")

    def build_requirements(self):
        if Version(self.version) >= "2.5.1":
            self.tool_requires("cmake/[>=3.23 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SI_BUILD_TESTING"] = False
        tc.variables["SI_BUILD_DOC"] = False
        tc.variables["SI_INSTALL_LIBRARY"] = True
        tc.generate()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "SI")
        self.cpp_info.set_property("cmake_target_name", "SI::SI")

        self.cpp_info.names["cmake_find_package"] = "SI"
        self.cpp_info.names["cmake_find_package_multi"] = "SI"
