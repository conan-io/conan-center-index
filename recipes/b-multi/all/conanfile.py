from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os


class MultiConan(ConanFile):
    name = "b-multi"
    homepage = "https://gitlab.com/correaa/boost-multi"
    description = "Multidimensional array access to contiguous or regularly contiguous memory. (Not an official Boost library)"
    topics = (
        "array",
        "multidimensional",
        "library",
    )
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    no_copy_source = True

	@property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {"gcc": "8",
                "clang": "7",
                "apple-clang": "12",
                "Visual Studio": "16",
                "msvc": "192"}

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*.hpp", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "multi")
        self.cpp_info.set_property("cmake_target_name", "multi::multi")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
