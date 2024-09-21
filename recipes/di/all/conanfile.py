import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, save, load
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class DiConan(ConanFile):
    name = "di"
    description = "DI: C++14 Dependency Injection Library."
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/boost-ext/di"
    topics = ("dependency-injection", "metaprogramming", "design-patterns", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_extensions": [True, False],
        "diagnostics_level": [0, 1, 2]
    }
    default_options = {
        "with_extensions": False,
        "diagnostics_level": 1
    }
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191"
        }

    def configure(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        compiler = str(self.settings.compiler)
        if compiler not in self._compilers_minimum_version:
            self.output.warning(
                f"{self.name} recipe lacks information about the {compiler} compiler standard version support")
            self.output.warning(
                f"{self.name} requires a compiler that supports at least C++{self._min_cppstd}")
            return
        version = Version(self.settings.compiler.version)
        if version < self._compilers_minimum_version[compiler]:
            raise ConanInvalidConfiguration(
                f"{self.name} requires a compiler that supports at least C++{self._min_cppstd}")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.requires.clear()
        self.info.settings.clear()
        del self.info.options.diagnostics_level

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _extract_license(self):
        file = os.path.join(self.source_folder, "CMakeLists.txt")
        file_content = load(self, file)

        license_start = file_content.find("# Copyright")
        sub_end = "LICENSE_1_0.txt)"
        license_end = file_content.find(sub_end)
        license_contents = file_content[license_start:(license_end + len(sub_end))]
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)


    def package(self):
        self._extract_license()
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.options.with_extensions:
            copy(self, "*.hpp",
                 dst=os.path.join(self.package_folder, "include", "boost", "di", "extension"),
                 src=os.path.join(self.source_folder, "extension", "include", "boost", "di", "extension"),
                 keep_path=True)
        copy(self, "di.hpp",
             dst=os.path.join(self.package_folder, "include", "boost"),
             src=os.path.join(self.source_folder, "include", "boost"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.defines.append(
            f"BOOST_DI_CFG_DIAGNOSTICS_LEVEL={self.options.diagnostics_level}")
