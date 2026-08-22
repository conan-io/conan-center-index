from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd, check_max_cppstd
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


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

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 17)
        if self.settings.compiler in ["apple-clang", "clang"]:
            if Version(self.settings.compiler.version) < "15":
                # error: reference to local binding 'tag' declared in enclosing function 'parlay::parlay_hash::Find'
                raise ConanInvalidConfiguration(f"Can't be used with {self.settings.compiler} < 15, lacks proper C++17 support")
            else:
                # error: no type named 'result_of' in namespace 'std'
                check_max_cppstd(self, 17)
        if self.settings.compiler == "msvc":
            # error C3861: '__builtin_prefetch': identifier not found
            raise ConanInvalidConfiguration("Can't be used with msvc")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"), excludes=[".#hash_table.h"])

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")

        # This one is a best-effort guess, as the library is header-only it does not mention a target explicitly
        self.cpp_info.set_property("cmake_file_name", "parlayhash")
        self.cpp_info.set_property("cmake_target_name", "parlay")
