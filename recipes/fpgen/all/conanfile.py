import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class FpgenConan(ConanFile):
    name = "fpgen"
    description = "Functional programming in C++ using C++20 coroutines."
    license = ["MPL2"]
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jay-tux/fpgen/"
    topics = ("generators", "coroutines", "c++20", "header-only", "functional-programming", "functional")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "clang": "13",
            "apple-clang": "13.1",
            "Visual Studio": "16",
            "msvc": "192",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler == "clang" and not self.settings.compiler.libcxx == "libc++":
            raise ConanInvalidConfiguration(f"Use 'compiler.libcxx=libc++' with Clang for {self.name}.")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def lazy_lt_semver(v1, v2):
            # Needed to allow version "13" >= "13.1" for apple-clang
            return all(int(p1) < int(p2) for p1, p2 in zip(v1.split("."), v2.split(".")))

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*.hpp",
             dst=os.path.join(self.package_folder, "include", "fpgen"),
             src=self.source_folder,
             keep_path=False)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.includedirs.append(os.path.join("include", "fpgen"))
