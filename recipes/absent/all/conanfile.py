from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

import os

required_conan_version = ">=1.53.0"


class AbsentConan(ConanFile):
    name = "absent"
    description = (
        "A small C++17 library meant to simplify the composition of nullable "
        "types in a generic, type-safe, and declarative way"
    )
    homepage = "https://github.com/rvarago/absent"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    topics = ("nullable-types", "composition", "monadic-interface", "declarative-programming")
    package_type = "header-library"
    no_copy_source = True
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
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        # header_only - no build

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "absent")
        self.cpp_info.set_property("cmake_target_name", "rvarago::absent")
        self.cpp_info.components["absentlib"].set_property("cmake_target_name", "rvarago::absent")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["absentlib"].bindirs = []
        self.cpp_info.components["absentlib"].frameworkdirs = []
        self.cpp_info.components["absentlib"].libdirs = []
        self.cpp_info.components["absentlib"].resdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "absent"
        self.cpp_info.filenames["cmake_find_package_multi"] = "absent"
        self.cpp_info.names["cmake_find_package"] = "rvarago"
        self.cpp_info.names["cmake_find_package_multi"] = "rvarago"
        self.cpp_info.components["absentlib"].names["cmake_find_package"] = "absent"
        self.cpp_info.components["absentlib"].names["cmake_find_package_multi"] = "absent"
