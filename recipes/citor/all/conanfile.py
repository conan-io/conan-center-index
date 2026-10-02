from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0"


class CitorConan(ConanFile):
    name = "citor"
    description = "Header-only C++20 thread pool with sub-microsecond dispatch, decentralized work-stealing, and per-CCD arenas."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Lallapallooza/citor"
    topics = ("concurrency", "cpp20", "fork-join", "low-latency", "multithreading", "parallel-computing", "thread-pool", "work-stealing", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {
            # <coroutine> needs -fcoroutines before GCC 11
            "gcc": "11",
            # Lambda captures of structured bindings need Clang 16
            "clang": "16",
            "apple-clang": "15",
            # Upstream CI tests Visual Studio 2022
            "msvc": "193",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        # INFO: Upstream validates only Linux x86_64 and Windows x86_64.
        # See https://github.com/Lallapallooza/citor#supported-targets
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration(f"{self.ref} supports only x86_64.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
        copy(self, "citor.hpp", os.path.join(self.source_folder, "single_include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "citor")
        self.cpp_info.set_property("cmake_target_name", "citor::citor")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
