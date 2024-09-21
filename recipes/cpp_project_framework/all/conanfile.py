import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class CppProjectFrameworkConan(ConanFile):
    name = "cpp_project_framework"
    description = "C++ Project Framework is a framework for creating C++ projects."
    license = "AGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sheepgrass/cpp_project_framework"
    topics = ("cpp", "project", "framework", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.os not in ("Linux", "FreeBSD", "Windows"):
            raise ConanInvalidConfiguration(f"{self.name} is only supported on Linux and Windows")

        compiler = self.settings.compiler

        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        if compiler in ("gcc", "clang"):
            if not compiler.get_safe("libcxx", "").startswith("libstdc++"):
                raise ConanInvalidConfiguration(f"{self.name} is only supported {compiler} with libstdc++")

        min_version = self._minimum_compilers_version.get(str(compiler))
        if not min_version:
            self.output.warning(f"{self.name} recipe lacks information about the {compiler} compiler support.")
        else:
            if Version(compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires C++{self._minimum_cpp_standard} support. "
                    f"The current compiler {compiler} {compiler.version} does not support it."
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*.h",
             dst=os.path.join(self.package_folder, "include", self.name),
             src=os.path.join(self.source_folder, self.name))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
