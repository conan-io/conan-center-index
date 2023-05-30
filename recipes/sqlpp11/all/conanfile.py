import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.33.0"


class Sqlpp11Conan(ConanFile):
    name = "sqlpp11"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rbock/sqlpp11"
    description = "A type safe SQL template library for C++"
    topics = ("sql", "dsl", "embedded", "data-base")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cpp_standard(self):
        return 11 if Version(self.version) < "0.61" else 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "14",
            "clang": "3.4",
            "apple-clang": "10",
        }

    def requirements(self):
        self.requires("date/3.0.0")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cpp_standard)

        if self._min_cpp_standard > 11:
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version:
                if Version(self.settings.compiler.version) < minimum_version:
                    raise ConanInvalidConfiguration(f"{self.name} requires C++14, which your compiler does not support.")
            else:
                self.output.warning(f"{self.name} requires C++14. Your compiler is unknown. Assuming it supports C++14.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        pass

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
        copy(self, "*", os.path.join(self.source_folder, "scripts"), os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_package", "Sqlpp11")
        self.cpp_info.set_property("cmake_find_package_multi", "Sqlpp11")
        self.cpp_info.set_property("pkg_config_name", "sqlpp11")
        self.cpp_info.libdirs = []

        bindir = os.path.join(self.package_folder, "bin")
        self.cpp_info.bindirs = [bindir]
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
