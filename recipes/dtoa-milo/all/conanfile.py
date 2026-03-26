from conan import ConanFile
from conan.tools.files import get, copy, apply_conandata_patches, export_conandata_patches
import os

required_conan_version = ">=2.0"

class DtoaMiloConan(ConanFile):
    name = "dtoa-milo"
    version = "1.0"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/miloyip/dtoa-benchmark"
    description = "Milo Yip's fast double-to-ascii (dtoa) implementation — header-only"
    topics = ("dtoa", "double", "float", "conversion", "header-only")
    package_type = "header-library"
    languages = "C++"
    no_copy_source = True

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, "license.txt", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "dtoa_milo.h", src=os.path.join(self.source_folder, "src", "milo"),
             dst=os.path.join(self.package_folder, "include", "dtoa-milo"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "dtoa-milo")
        self.cpp_info.set_property("cmake_target_name", "dtoa-milo::dtoa-milo")

    def package_id(self):
        self.info.clear()
