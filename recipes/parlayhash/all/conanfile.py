from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rm
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"


class ParlayHashConan(ConanFile):
    name = "parlayhash"
    description = "A Header-Only Scalable Concurrent Hash Map."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cmuparlay/parlayhash"
    topics = ("unordered_map", "hashmap", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15.7",
            "msvc": "191",
            "gcc": "7",
            "clang": "7",
            "apple-clang": "11",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        # TODO: Upstream mentions jemalloc in https://github.com/cmuparlay/parlayhash/blob/main/CMakeLists.txt#L45
        #     but it's not ported to Conan 2 yet. Add it here if needed in the future.
        pass

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.get_safe("compiler.version")) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        rm(self, "#hash_table.h#", os.path.join(self.source_folder, "include", "parlay"))
        rm(self, "#primitives.h#", os.path.join(self.source_folder, "include", "parlay"))
        rm(self, ".#hash_table.h", os.path.join(self.source_folder, "include", "parlay"))

    def build(self):
        pass

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")

        # This one is a best-effort guess, as the library is header-only it does not mention a target explicitly
        self.cpp_info.set_property("cmake_file_name", "parlay_hash")
        self.cpp_info.set_property("cmake_target_name", "parlay")
