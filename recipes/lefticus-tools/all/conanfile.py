from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd, check_min_vs
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration
from conan import Version
import os


required_conan_version = ">=1.53.0"


class LefticusToolsConan(ConanFile):
    name = "lefticus-tools"
    description = "Some handy C++ tools"
    topics = ("tools", "cpp", "cmake")
    license = "MIT"
    homepage = "https://github.com/lefticus/tools"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "clang": "13",
            "apple-clang": "14",
        }

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 192)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="ProjectOptions", dst=os.path.join(self.package_folder, "lib", "cmake"), src=self.source_folder)
        copy(self, pattern="*.cmake", dst=os.path.join(self.package_folder, "lib", "cmake", "cmake"), src=os.path.join(self.source_folder, "cmake"))
        copy(self, pattern="*.hpp", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "lefticus::tools")
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
