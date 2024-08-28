from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.51.1"

class GlazeConan(ConanFile):
    name = "glaze"
    description = "Extremely fast, in memory, JSON and interface library for modern C++"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/stephenberry/glaze"
    topics = ("json", "memory", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "20" if Version(self.version) < "3.0.0" else "23"

    @property
    def _compilers_minimum_version(self):
        return {
            "20": {
                "Visual Studio": "17",
                "msvc": "193",
                "gcc": "11" if Version(self.version) < "2.6.3" else "12",
                "clang": "14",
                "apple-clang": "13.1",
            },
            "23": {
                "Visual Studio": "17",
                "msvc": "193",
                "gcc": "12",
                "clang": "15",
                "apple-clang": "14",
            },
        }.get(self._min_cppstd, {})

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        # remove this block when all versions of under 2.6.3 will be removed.
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "11.3":
            raise ConanInvalidConfiguration(
                f"{self.ref} doesn't support 11.0<=gcc<11.3 due to gcc bug. Please use gcc>=11.3 and set compiler.version.(ex. compiler.version=11.3)",
            )

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if is_msvc(self):
            self.cpp_info.cxxflags.append("/Zc:preprocessor")
