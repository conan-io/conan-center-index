from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os
import re

required_conan_version = ">=1.52.0"

class UvwConan(ConanFile):
    name = "uvw"
    description = "Header-only, event based, tiny and easy to use libuv wrapper in modern C++."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/skypjack/uvw"
    topics = ("libuv", "io", "networking", "header-only",)
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
            "clang": "5",
            "apple-clang": "10",
        }
    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        # Check whether the version of libuv used as a requirement is ok
        required_version = self._required_EXACT_libuv_version
        tuple_exact = (required_version.major, required_version.minor)

        current_version = Version(self.dependencies["libuv"].ref.version)
        tuple_current = (current_version.major, current_version.minor)

        if tuple_exact != tuple_current:
            raise ConanException("This version of uvw requires an exact libuv version as dependency: {}.{}".format(
                    required_version.major,
                    required_version.minor)
                )


    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _required_EXACT_libuv_version(self):
        """ Return *EXACT* libuv version to use with this uvw library """
        match = re.match(r".*libuv[_-]v([0-9]+\.[0-9]+).*", self.conan_data["sources"][self.version]["url"])
        if not match:
            raise ConanException("uvw recipe does not know what version of libuv to use as dependency")
        return Version(match.group(1))

    def requirements(self):
        libuv_version = self._required_EXACT_libuv_version
        revision = 0
        if libuv_version.major == "1" and libuv_version.minor == "44":
            revision = 1
        self.requires("libuv/{}.{}.{}".format(libuv_version.major, libuv_version.minor, revision))

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "src"),
        )
        copy(
            self,
            pattern="*",
            dst=os.path.join(self.package_folder, "include", "uvw"),
            src=os.path.join(self.source_folder, "src", "uvw"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
