from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class LibmortonConan(ConanFile):
    name = "libmorton"
    description = "C++ header-only library with methods to efficiently " \
                  "encode/decode 64, 32 and 16-bit Morton codes and coordinates, in 2D and 3D."
    license = "MIT"
    topics = ("libmorton", "morton", "encoding", "decoding")
    homepage = "https://github.com/Forceflow/libmorton"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if Version(self.version) < "0.2.7":
            src_hdrs = os.path.join(self.source_folder, "libmorton", "include")
        elif Version(self.version) < "0.2.8":
            src_hdrs = os.path.join(self.source_folder, "libmorton")
        else:
            src_hdrs = os.path.join(self.source_folder, "include", "libmorton")
        copy(self, "*.h", src=src_hdrs, dst=os.path.join(self.package_folder, "include", "libmorton"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libmorton")
        self.cpp_info.set_property("cmake_target_name", "libmorton::libmorton")
        self.cpp_info.set_property("pkg_config_name", "libmorton")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
