from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import export_conandata_patches, get, copy
import os

required_conan_version = ">=1.52.0"

class CloveUnitConan(ConanFile):
    name = "clove-unit"
    description = "Single-header Unit Testing framework for C (interoperable with C++) with test autodiscovery feature"
    topics = ("clove-unit", "unit-testing", "testing", "unit testing", "test")
    homepage = "https://github.com/fdefelici/clove-unit"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    no_copy_source = True
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    # Use the export_sources(self) method instead of the exports_sources attribute.
    # This allows finer grain exportation of patches per version
    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    # Not mandatory when there is no patch, but will suppress warning message about missing build() method
    def build(self):
        # The attribute no_copy_source should not be used when applying patches in build
        # apply_conandata_patches(self)
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "clove-unit.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CloveUnit")
        self.cpp_info.set_property("cmake_target_name", "CloveUnit::CloveUnit")
        # Folders not used for header-only
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        # NOTE: needed by conan test phase on test_v1_package folder
        self.cpp_info.filenames["cmake_find_package"] = "CloveUnit"
        self.cpp_info.filenames["cmake_find_package_multi"] = "CloveUnit"
        self.cpp_info.names["cmake_find_package"] = "CloveUnit"
        self.cpp_info.names["cmake_find_package_multi"] = "CloveUnit"
