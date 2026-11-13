import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout

required_conan_version = ">=2.0"


class KeypopCardCppApiConan(ConanFile):
    name = "keypop-card-cpp-api"
    description = "C++ API defining the Eclipse Keypop Terminal Card interfaces"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eclipse-keypop/keypop-card-cpp-api"
    topics = ("smart-card", "calypso", "terminal-api", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    # Do not copy sources to build folder for header only projects, unless you need to apply patches
    no_copy_source = True

    # Use the export_sources(self) method instead of the exports_sources attribute.
    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    # same package ID for any package
    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    # Suppress warning message about missing build() method when running Conan
    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "keypop-card-cpp-api")
        self.cpp_info.set_property("cmake_target_name", "Keypop::Card")

        # Folders not used for header-only
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
