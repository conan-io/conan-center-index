from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "package"
    description = "short description"
    # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    # In case not listed there, use "LicenseRef-<license-file-name>"
    license = ""
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/project/package"
    # no "conan" and project name in topics. Use topics from the upstream listed on GH
    # Keep 'hearder-only' as topic
    topics = ("topic1", "topic2", "topic3", "header-only")
    settings = "os", "arch", "compiler", "build_type"  # even for header only
    no_copy_source = True  # do not copy sources to build folder for header only projects, unless, need to apply patches

    @property
    def _min_cppstd(self):
        return 14

    # in case the project requires C++14/17/20/... the minimum compiler version should be listed
    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "14.1",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }

    # no exports_sources attribute, but export_sources(self) method instead
    # this allows finer grain exportation of patches per version
    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        # src_folder must use the same source folder name the project
        basic_layout(self, src_folder="src")

    def requirements(self):
        # prefer self.requires method instead of requires attribute
        # direct dependencies of header only libs are always transitive since they are included in public headers
        self.requires("dependency/0.8.1", transitive_headers=True)

    # same package ID for any package
    def package_id(self):
        self.info.clear()

    @property
    def _info(self):
        return self if Version(conan_version).major < 2 else self.info

    def validate(self):
        # compiler subsettings are not available when building with self.info.clear()
        if self._info.settings.compiler.get_safe("cppstd"):
            # validate the minimum cpp standard supported when installing the package. For C++ projects only
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self._info.settings.compiler), False)
        if minimum_version and Version(self._info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        # in case it does not work in another configuration, it should validated here too
        if self._info.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} can not be used on Windows.")

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
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        # folders not used for header-only
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # if package has an official FindPACKAGE.cmake listed in https://cmake.org/cmake/help/latest/manual/cmake-modules.7.html#find-modules
        # examples: bzip2, freetype, gdal, icu, libcurl, libjpeg, libpng, libtiff, openssl, sqlite3, zlib...
        self.cpp_info.set_property("cmake_module_file_name", "PACKAGE")
        self.cpp_info.set_property("cmake_module_target_name", "PACKAGE::PACKAGE")
        # if package provides a CMake config file (package-config.cmake or packageConfig.cmake, with package::package target, usually installed in <prefix>/lib/cmake/<package>/)
        self.cpp_info.set_property("cmake_file_name", "package")
        self.cpp_info.set_property("cmake_target_name", "package::package")
        # if package provides a pkgconfig file (package.pc, usually installed in <prefix>/lib/pkgconfig/)
        self.cpp_info.set_property("pkg_config_name", "package")

        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "PACKAGE"
        self.cpp_info.filenames["cmake_find_package_multi"] = "package"
        self.cpp_info.names["cmake_find_package"] = "PACKAGE"
        self.cpp_info.names["cmake_find_package_multi"] = "package"
