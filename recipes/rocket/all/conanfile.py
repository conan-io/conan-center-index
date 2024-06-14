from conan import ConanFile
from conan.tools.files import copy, get, save, load
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=1.53.0"


class RocketConan(ConanFile):
    name = "rocket"
    description = "Fast single header signal/slots library for C++"
    license = "DocumentRef-README.md:LicenseRef-Rocket-public-domain"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tripleslash/rocket"
    topics = ("signal-slots", "observer-pattern")
    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _min_cppstd(self):
        return 11

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package_id(self):
        self.info.clear()

    def build(self):
        pass

    def _extract_license(self):
        readme_content = load(self, os.path.join(self.source_folder, "README.md"))
        license_content = "\n".join(readme_content.splitlines()[:6])
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_content)

    def package(self):
        self._extract_license()
        copy(self, "rocket.hpp", self.build_folder, os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

