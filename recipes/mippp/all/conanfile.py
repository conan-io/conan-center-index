import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=2.1"


class MipppConan(ConanFile):
    name = "mippp"
    description = "Header-only C++23 library for linear, mixed-integer and quadratic programming solvers."
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/fhamonic/mippp"
    topics = ("header-only", "linear-programming", "mip", "linear-programming",
              "operations-research", "optimization", "template-metaprogramming")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 23)
        compilers = {"gcc": "14", "clang": "18", "apple-clang": "21", "msvc": "194"}
        if str(self.settings.compiler) in compilers and Version(self.settings.compiler.version) < compilers[str(self.settings.compiler)]:
            raise ConanInvalidConfiguration(f"{self.settings.compiler} version must be at least {compilers[str(self.settings.compiler)]}. See https://github.com/fhamonic/mippp#installation")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        # Solvers are dlopen()'d (detail/dynamic_library.hpp). On glibc < 2.34 (RHEL 8,
        # manylinux_2_28, conda-forge sysroots) dlopen() is in libdl: without `dl`, any
        # consumer instantiating a solver fails with "undefined reference to dlopen".
        # glibc >= 2.34 folds libdl into libc, so the omission is invisible there.
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("dl")
