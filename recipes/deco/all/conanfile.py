import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class DecoConan(ConanFile):
    name = "deco"
    description = "Delimiter Collision Free Format"
    license = "Apache-2.0-WITH-LLVM-exception"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Enhex/Deco"
    topics = ("serialization", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "7",
            "clang": "5.0",
            "apple-clang": "9.1",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("enhex-generic_serialization/1.0.0")
        self.requires("enhex-strong_type/1.0.0")
        self.requires("boost/1.82.0")
        self.requires("rang/3.2")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version)

        if compiler not in self._compilers_minimum_version:
            self.output.info(f"{self.name} requires a compiler that supports at least C++17")
            return

        # Exclude compilers not supported
        if compiler_version < self._compilers_minimum_version[compiler]:
            raise ConanInvalidConfiguration(
                f"{self.name} requires a compiler that supports at least C++17. "
                f"{compiler} {Version(self.settings.compiler.version.value)} is not"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
