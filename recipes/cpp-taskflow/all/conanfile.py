import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class CppTaskflowConan(ConanFile):
    name = "cpp-taskflow"
    description = "A fast C++ header-only library to help you quickly write parallel programs with complex task dependencies."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cpp-taskflow/cpp-taskflow"
    topics = ("taskflow", "tasking", "parallelism", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    deprecated = "taskflow"

    @property
    def _min_cppstd(self):
        return 17 if Version(self.version) <= "2.2.0" else 14

    @property
    def _compilers_minimum_version(self):
        return {
            17: {
                "Visual Studio": "16",
                "gcc": "7.3",
                "clang": "6.0",
                "apple-clang": "10.0",
            },
            14: {
                "Visual Studio": "15",
                "gcc": "5",
                "clang": "4.0",
                "apple-clang": "8.0",
            }
        }[self._min_cppstd]

    def validate(self):
        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version)

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        else:
            self.output.warning(f"{self.name} recipe lacks information about the {compiler} compiler standard version support")

        if compiler not in self._compilers_minimum_version:
            self.output.info(f"{self.name} requires a compiler that supports at least C++{self._min_cppstd}")
            return

        # Exclude compilers not supported by cpp-taskflow
        if compiler_version < self._compilers_minimum_version[compiler]:
            raise ConanInvalidConfiguration(
                f"{self.name} requires a compiler that supports at least C++{self._min_cppstd}."
                f" {compiler} {Version(self.settings.compiler.version.value)} is not supported."
            )

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*",
             dst=os.path.join(self.package_folder, "include/taskflow"),
             src=os.path.join(self.source_folder, "taskflow"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if is_msvc(self):
            self.cpp_info.defines.append("_ENABLE_EXTENDED_ALIGNED_STORAGE")
