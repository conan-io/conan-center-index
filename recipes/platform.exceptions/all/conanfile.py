import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class PlatformExceptionsConan(ConanFile):
    name = "platform.exceptions"
    description = "platform.exceptions is one of the libraries of the LinksPlatform modular framework, to ensure exceptions"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/linksplatform/Exceptions"
    topics = ("linksplatform", "cpp20", "exceptions", "any", "ranges", "native", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 20

    @property
    def _internal_cpp_subfolder(self):
        return os.path.join(self.source_folder, "cpp", "Platform.Exceptions")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10",
            "Visual Studio": "16",
            "clang": "11",
            "apple-clang": "11",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) >= "0.3.0":
            self.requires("platform.delegates/0.3.7")
        else:
            self.requires("platform.delegates/0.1.3")

    def package_id(self):
        self.info.clear()

    def validate(self):
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))

        if not minimum_version:
            self.output.warning(f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support.")

        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.name}/{self.version} requires c++{self._minimum_cpp_standard}, which is not supported"
                f" by {self.settings.compiler} {self.settings.compiler.version}."
            )

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*.h",
             dst=os.path.join(self.package_folder, "include"),
             src=self._internal_cpp_subfolder)
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
