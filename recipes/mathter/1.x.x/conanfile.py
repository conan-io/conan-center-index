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
    options = {
        "with_xsimd": [True, False] # XSimd is optionally used for hand-rolled vectorization.
    }
    default_options = {
        "with_xsimd": True
    }
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
    
    def config_options(self):
        if Version(self.version) < "1.1":
            del self.options.with_xsimd

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.name} requires C++{self._min_cppstd}, "
                                            "which your compiler does not support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        if self.options.get_safe("with_xsimd"):
            self.requires("xsimd/11.1.0")

    def package(self):
        if self.version == "1.0.0":
            copy(self, "LICENCE", self.source_folder, os.path.join(self.package_folder, "licenses"))
            include_dir = os.path.join(self.source_folder, "Mathter")
        else:
            copy(self, "LICENCE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
            include_dir = os.path.join(self.source_folder, "include", "Mathter")
        copy(self, "*.hpp", include_dir, os.path.join(self.package_folder, "include", "Mathter"))
        copy(self, "*.natvis", include_dir, os.path.join(self.package_folder, "include", "Mathter"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.options.get_safe("with_xsimd"):
            self.cpp_info.defines = ["MATHTER_USE_XSIMD=1"]
