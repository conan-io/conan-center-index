import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.43.0"


class BShoshanyThreadPoolConan(ConanFile):
    name = "bshoshany-thread-pool"
    description = "BS::thread_pool: a fast, lightweight, modern, and easy-to-use C++17 / C++20 / C++23 thread pool library"
    homepage = "https://github.com/bshoshany/thread-pool"
    license = "MIT"
    topics = ("concurrency", "cpp17", "cpp20", "cpp23", "header-only", "library", "multi-threading", "parallel-computing", "thread-pool", "threads", "module", "modules")
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "header-library"
    settings = "arch", "build_type", "compiler", "os"
    no_copy_source = True

    @property
    def _minimum_compilers_version(self):
        return {
            "apple-clang": "10",
            "clang": "5",
            "gcc": "8",
            "Visual Studio": "16",
            "msvc": "192",
        }

    @property
    def _min_cppstd(self):
        return "17"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        if Version(self.version) < "3.5.0":
            copy(self, "*.hpp", self.source_folder, os.path.join(self.package_folder, "include"))
        elif Version(self.version) < "5.0.0":
            copy(self, "*.hpp", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
        else:
            copy(self, "BS_thread_pool.hpp", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
            copy(self, "BS.thread_pool.cppm", os.path.join(self.source_folder, "modules"), os.path.join(self.package_folder, "modules"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
