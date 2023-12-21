import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class MathterConan(ConanFile):
    name = "mathter"
    description = "Powerful 3D math and small-matrix linear algebra library for games and science."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/petiaccja/Mathter"
    topics = ("game-dev", "linear-algebra", "vector-math", "matrix-library", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": 10,
            "clang": 6,
            "gcc": 7,
            "Visual Studio": 16,
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.name} requires C++{self._min_cppstd}, "
                                                f"which your compiler does not support.")
        else:
            self.output.warning(f"{self.name} requires C++{self._min_cppstd}. "
                                f"Your compiler is unknown. Assuming it supports C++{self._min_cppstd}.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*.hpp",
             dst=os.path.join(self.package_folder, "include", "Mathter"),
             src=os.path.join(self.source_folder, "Mathter"))
        copy(self, "*.natvis",
             dst=os.path.join(self.package_folder, "include", "Mathter"),
             src=os.path.join(self.source_folder, "Mathter"))
        copy(self, "LICENCE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
