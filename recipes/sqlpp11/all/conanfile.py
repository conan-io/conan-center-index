from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class Sqlpp11Conan(ConanFile):
    name = "sqlpp11"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rbock/sqlpp11"
    description = "A type safe SQL template library for C++"
    topics = ("sql", "dsl", "embedded", "data-base")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11 if Version(self.version) < "0.61" else 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "14",
            "msvc": "190",
            "clang": "3.4",
            "apple-clang": "10",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("date/3.0.1")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
        copy(self, "*", dst=os.path.join(self.package_folder, "bin"), src=os.path.join(self.source_folder, "scripts"))

    def package_info(self):
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "Sqlpp11")
        self.cpp_info.set_property("cmake_target_name", "sqlpp11::sqlpp11")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
