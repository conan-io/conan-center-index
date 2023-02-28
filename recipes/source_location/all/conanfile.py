import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class SourceLocationConan(ConanFile):
    name = "source_location"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Rechip/source_location"
    description = "source_location header for some older compilers"
    topics = ("cpp", "source_location", "header-only")
    settings = ["compiler"]
    no_copy_source = True

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"), keep_path=False)

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16.6",
            "gcc": "7.1",
            "clang": "9",
            "apple-clang": "12",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "11")
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("source_location requires C++11. Your compiler is unknown. Assuming it supports C++11 and required functionality.")
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("source_location requires C++11 and some embedded functionality, which your compiler does not support.")

    def package_id(self):
        self.info.clear()
