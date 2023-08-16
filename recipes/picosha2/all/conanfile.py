from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, load, save
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"

class PicoSHA2Conan(ConanFile):
    name = "picosha2"
    description = "a header-file-only, SHA256 hash generator in C++ "
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/okdshin/PicoSHA2"
    topics = ("sha256", "hash", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        if Version(self.version) == "1.0.0":
            filename = os.path.join(self.source_folder, self.source_folder, "picosha2.h")
            file_content = load(save, filename)
            license_start = "/*"
            license_end = "*/"
            license_contents = file_content[file_content.find(license_start)+len(license_start):file_content.find(license_end)]
            save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)
        else:
            copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=self.source_folder,
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
