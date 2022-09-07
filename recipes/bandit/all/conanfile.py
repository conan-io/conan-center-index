from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.51.3"


class BanditConan(ConanFile):
    name = "bandit"
    description = "Human-friendly unit testing for C++11"
    topics = ("testing", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/banditcpp/bandit"
    license = "MIT"
    no_copy_source = True

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def requirements(self):
        self.requires("snowhouse/5.0.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def layout(self):
        basic_layout(self)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, "LICENSE.txt", src=os.path.join(self.source_folder, "docs"), dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "include", "bandit"), src=os.path.join(self.source_folder, "bandit"))

    def package_id(self):
        self.info.clear()
