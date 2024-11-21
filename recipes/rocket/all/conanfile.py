from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, load, save
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class RocketConan(ConanFile):
    name = "rocket"
    description = "Fast single header signal/slots library for C++"
    license = "DocumentRef-README.md:LicenseRef-Rocket-public-domain"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tripleslash/rocket"
    topics = ("signal-slots", "observer-pattern", "header-only")
    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package_id(self):
        self.info.clear()

    def build(self):
        apply_conandata_patches(self)

    def _extract_license(self):
        readme_content = load(self, os.path.join(self.source_folder, "README.md"))
        first = readme_content.find("# rocket")
        last = readme_content.find("signals2).")
        license_content = readme_content[first:last+len("signals2).")]
        # Make sure the extracted text from README has the license type
        assert license_content.find("public-domain") != -1
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_content)

    def package(self):
        self._extract_license()
        copy(self, "rocket.hpp", self.build_folder, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

