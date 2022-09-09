from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, get, load, save
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.50.0"


class GetoptForVisualStudioConan(ConanFile):
    name = "getopt-for-visual-studio"
    description = "GNU getopt for Visual Studio"
    topics = ("getopt", "cli", "command line", "options")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/skandhurkat/Getopt-for-Visual-Studio"
    license = "MIT", "BSD-2-Clause"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if not is_msvc(self):
            raise ConanInvalidConfiguration("getopt-for-visual-studio is only supported for Visual Studio")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

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
        self.cpp_info.resdirs = []
