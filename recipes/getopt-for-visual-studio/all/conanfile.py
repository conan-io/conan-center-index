from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, load, save
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.52.0"


class GetoptForVisualStudioConan(ConanFile):
    name = "getopt-for-visual-studio"
    description = "GNU getopt for Visual Studio"
    topics = ("getopt", "cli", "command line", "options")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/skandhurkat/Getopt-for-Visual-Studio"
    license = "MIT", "BSD-2-Clause"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if not is_msvc(self):
            raise ConanInvalidConfiguration("getopt-for-visual-studio is only supported for Visual Studio")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    @property
    def _license_text(self):
        content = load(self, os.path.join(self.source_folder, "getopt.h"))
        return "\n".join(list(l.strip() for l in content[content.find("/**", 3):content.find("#pragma")].split("\n")))

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._license_text)
        copy(self, "getopt.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
