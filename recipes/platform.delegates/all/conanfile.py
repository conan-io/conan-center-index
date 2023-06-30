import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class PlatformDelegatesConan(ConanFile):
    name = "platform.delegates"
    description = (
        "platform.delegates is one of the libraries of the LinksPlatform modular framework, which uses"
        " innovations from the C++17 standard, for easier use delegates/events in csharp style."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/linksplatform/Delegates"
    topics = ("linksplatform", "cpp17", "delegates", "events", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _internal_cpp_subfolder(self):
        return os.path.join(self.source_folder, "cpp", "Platform.Delegates")

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "Visual Studio": "16",
            "clang": "14",
            "apple-clang": "14",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))

        if not minimum_version:
            self.output.warning(f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support.")

        if Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"platform.delegates/{self.version} requires C++{self._minimum_cpp_standard} with"
                f" {self.settings.compiler}, which is not supported by"
                f" {self.settings.compiler} {self.settings.compiler.version}."
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
