from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "gmtl"
    description = "Generic Math Template Library"
    # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    # In case not listed there, use "LicenseRef-<license-file-name>"
    license = "LGPL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ggt.sourceforge.net/html/main.html"
    # no "conan" and project name in topics. Use topics from the upstream listed on GH
    # Keep 'hearder-only' as topic
    topics = ("linear-algebra", "collision", "vector", "matrix", "template", "math", "header-only")
    settings = "os", "arch", "compiler", "build_type"  # even for header only
    no_copy_source = True  # do not copy sources to build folder for header only projects, unless, need to apply patches

    # no exports_sources attribute, but export_sources(self) method instead
    # this allows finer grain exportation of patches per version
    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        # src_folder must use the same source folder name the project
        basic_layout(self, src_folder="gmtl")

    def requirements(self):
        # prefer self.requires method instead of requires attribute
        return
        
    # same package ID for any package
    def package_id(self):
        self.info.clear()

    def validate(self):
        # compiler subsettings are not available when building with self.info.clear()
        return

    # if another tool than the compiler or CMake is required to build the project (pkgconf, bison, flex etc)
    def build_requirements(self):
        return

    def source(self):
        # download source package and extract to source folder
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    # not mandatory when there is no patch, but will suppress warning message about missing build() method
    def build(self):
        # The attribute no_copy_source should not be used when applying patches in build
        apply_conandata_patches(self)

    # copy all files to the package folder
    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "."),
        )

    def package_info(self):
        # folders not used for header-only
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

  
