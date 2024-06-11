from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "package"
    description = "short description"
    # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    # In case it's not listed there, use "LicenseRef-<license-file-name>"
    license = ""
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/project/package"
    # Do not put "conan" nor the project name in topics. Use topics from the upstream listed on GH
    # Keep 'header-only' as topic
    topics = ("topic1", "topic2", "topic3", "header-only")
    package_type = "header-library"
    # Keep these or explain why it's not required for this particular case
    settings = "os", "arch", "compiler", "build_type"
    # Do not copy sources to build folder for header only projects, unless you need to apply patches
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 14

    # In case the project requires C++14/17/20/... the minimum compiler version should be listed
    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15",
        }

    # Use the export_sources(self) method instead of the exports_sources attribute.
    # This allows finer grain exportation of patches per version
    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        # src_folder must use the same source folder name than the project
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Prefer self.requires method instead of requires attribute
        # Direct dependencies of header only libs are always transitive since they are included in public headers
        self.requires("dependency/0.8.1", transitive_headers=True)

    # same package ID for any package
    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            # Validate the minimum cpp standard supported when installing the package. For C++ projects only
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        # In case this library does not work in some another configuration, it should be validated here too
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} can not be used on Windows.")

    def source(self):
        # Download source package and extract to source folder
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    # Not mandatory when there is no patch, but will suppress warning message about missing build() method
    def build(self):
        # The attribute no_copy_source should not be used when applying patches in build
        apply_conandata_patches(self)

    # Copy all files to the package folder
    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(
            self,
            "*.h",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        # Folders not used for header-only
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # Set these to the appropriate values if the package has an official FindPACKAGE.cmake
        # listed in https://cmake.org/cmake/help/latest/manual/cmake-modules.7.html#find-modules
        # examples: bzip2, freetype, gdal, icu, libcurl, libjpeg, libpng, libtiff, openssl, sqlite3, zlib...
        self.cpp_info.set_property("cmake_module_file_name", "PACKAGE")
        self.cpp_info.set_property("cmake_module_target_name", "PACKAGE::PACKAGE")
        # Set these to the appropriate values if package provides a CMake config file
        # (package-config.cmake or packageConfig.cmake, with package::package target, usually installed in <prefix>/lib/cmake/<package>/)
        self.cpp_info.set_property("cmake_file_name", "package")
        self.cpp_info.set_property("cmake_target_name", "package::package")
        # Set this to the appropriate value if the package provides a pkgconfig file
        # (package.pc, usually installed in <prefix>/lib/pkgconfig/)
        self.cpp_info.set_property("pkg_config_name", "package")

        # Add m, pthread and dl if needed in Linux/FreeBSD
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "PACKAGE"
        self.cpp_info.filenames["cmake_find_package_multi"] = "package"
        self.cpp_info.names["cmake_find_package"] = "PACKAGE"
        self.cpp_info.names["cmake_find_package_multi"] = "package"
