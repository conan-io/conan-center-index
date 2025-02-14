import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, download

required_conan_version = ">=2.0"


class PackageConan(ConanFile):
    name = "stacktrace"
    description = "Print stack backtrace programmatically with demangled function names"
    license = "WTFPL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://panthema.net/2008/0901-stacktrace-demangled/"
    topics = ("stacktrace", "backtrace", "backtrace_symbols", "demangle", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def source(self):
        download(
            self,
            url="https://panthema.net/2008/0901-stacktrace-demangled/stacktrace.h",
            filename="stacktrace.h",
            sha256="f850b0b859595f26121ccc9c8b9a82d9ed9acfe35fdea01554b257e95301310b",
        )

    def export_sources(self):
        copy(self, "stacktrace.h", self.recipe_folder, self.export_sources_folder)

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 98)
        if str(self.settings.compiler) not in ["gcc", "clang"]:
            raise ConanInvalidConfiguration(
                f"{self.ref} does only demangle gcc and clang properly."
            )
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} might not compile on Windows.")

    def build(self):
        pass

    def package(self):
        copy(
            self,
            "stacktrace.h",
            self.source_folder,
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
