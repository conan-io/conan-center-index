import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class PlatformInterfacesConan(ConanFile):
    name = "platform.equality"
    description = (
        "platform.delegates is one of the libraries of the LinksPlatform modular framework, "
        "which uses innovations from the C++20 standard, for slow parody any typing dictionary and others."
    )
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/linksplatform/Equality"
    topics = ("linksplatform", "cpp20", "equality", "ranges", "any", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 20

    @property
    def _internal_cpp_subfolder(self):
        return os.path.join(self.source_folder, "cpp", "Platform.Equality")

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

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if not minimum_version:
            self.output.warning(f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support.")
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._minimum_cpp_standard} with {self.settings.compiler}, "
                f"which is not supported by {self.settings.compiler} {self.settings.compiler.version}."
            )

        if self.settings.compiler in ["clang", "apple-clang"] and not str(self.settings.compiler.libcxx).startswith("libstdc++"):
            # ranges library from libc++ is not compatible with platform.equality
            raise ConanInvalidConfiguration(f"{self.ref} requires libstdc++ with {self.settings.compiler}.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=self._internal_cpp_subfolder)
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
