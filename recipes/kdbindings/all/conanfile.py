from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.scm import Version
import os

class KDBindingsConan(ConanFile):
    name = "kdbindings"
    license = "MIT"
    topics = ("c++17", "reactive", "kdab", "header-only")
    description = "Reactive programming & data binding in C++"
    homepage = "https://github.com/KDAB/KDBindings"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    settings = "compiler"
    no_copy_source = True

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "clang": "7",
            "apple-clang": "11",
            "Visual Studio": "15.7",
            "msvc": "191",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++17, which your compiler does not support.")

    def build(self):
        pass

    def package(self):
        copy(self, "*.h", os.path.join(self.source_folder, "src","kdbindings"), os.path.join(self.package_folder, "include", "kdbindings"))
        copy(self, "LICENSES/*", dst=os.path.join(self.package_folder,"licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "KDBindings")
        self.cpp_info.set_property("cmake_target_name", "KDAB::KDBindings")
        self.cpp_info.set_property("cmake_target_aliases", ["KDBindings"])
