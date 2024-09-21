import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class ZugConan(ConanFile):
    name = "zug"
    description = "Transducers for C++ — Clojure style higher order push/pull sequence transformations"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sinusoid.es/zug/"
    topics = ("transducer", "algorithm", "signals", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "3.5",
            "apple-clang": "10",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        compiler = str(self.settings.compiler)
        if compiler not in self._compilers_minimum_version:
            self.output.warning("Unknown compiler, assuming it supports at least C++14")
            return

        version = Version(self.settings.compiler.version)
        if version < self._compilers_minimum_version[compiler]:
            raise ConanInvalidConfiguration(f"{self.name} requires a compiler that supports at least C++14")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*.hpp",
             dst=os.path.join(self.package_folder, "include", "zug"),
             src=os.path.join(self.source_folder, "zug"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if is_msvc(self):
            self.cpp_info.cxxflags = ["/Zc:externConstexpr"]
