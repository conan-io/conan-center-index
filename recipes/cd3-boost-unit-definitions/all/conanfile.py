from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.52.0"


class Cd3BoostUnitDefinitionsConan(ConanFile):
    name = "cd3-boost-unit-definitions"
    description = "A collection of pre-defined types and unit instances for working with Boost.Units quantities."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CD3/BoostUnitDefinitions"
    topics = ("physical dimensions", "header-only")
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
            "msvc": "191",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.80.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False
        )
        if (
            minimum_version
            and Version(self.settings.compiler.version) < minimum_version
        ):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(
            self,
            pattern="LICENSE.md",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "src"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "BoostUnitDefinitions")
        self.cpp_info.set_property(
            "cmake_target_name", "BoostUnitDefinitions::BoostUnitDefinitions"
        )

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "BoostUnitDefinitions"
        self.cpp_info.filenames["cmake_find_package_multi"] = "BoostUnitDefinitions"
        self.cpp_info.names["cmake_find_package"] = "BoostUnitDefinitions"
        self.cpp_info.names["cmake_find_package_multi"] = "BoostUnitDefinitions"
