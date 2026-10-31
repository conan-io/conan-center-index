from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=2.0"


class PerfectHashConan(ConanFile):
    name = "perfect_hash"
    description = "A compile-time perfect hash implementation"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ConstexprCore/perfect_hash"
    topics = ("hash", "hash-map", "hash-set", "compile-time", "constexpr", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 23

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "16",
            "clang": "16",
            "gcc": "12",
            "msvc": "194",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)
        compiler = str(self.settings.compiler)
        version = Version(self.settings.compiler.version)
        minimum_version = self._compilers_minimum_version.get(compiler, False)
        if minimum_version and version < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        # std::lexicographical_compare_three_way needs libc++ 17
        if compiler == "clang" and self.settings.get_safe("compiler.libcxx") == "libc++" and version < "17":
            raise ConanInvalidConfiguration(f"{self.ref} requires libc++ 17 or newer.")
        # 'if consteval' needs MSVC 19.44, but msvc 194 also covers 19.40-19.43
        update = self.settings.get_safe("compiler.update")
        if compiler == "msvc" and version == "194" and update is not None and int(update) < 4:
            raise ConanInvalidConfiguration(f"{self.ref} requires MSVC 19.44 or newer.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        # Upstream installs the amalgamated header to both locations
        singleheader = os.path.join(self.source_folder, "singleheader")
        copy(self, "perfect_hash.h", singleheader, os.path.join(self.package_folder, "include", "ConstexprCore"))
        copy(self, "perfect_hash.h", singleheader, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "perfect_hash")
        self.cpp_info.set_property("cmake_target_name", "ConstexprCore::perfect_hash")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
