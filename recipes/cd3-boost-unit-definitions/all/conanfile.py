from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import cmake_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "cd3-boost-unit-definitions"
    description = "A collection of pre-defined types and unit instances for working with Boost.Units quantities."
    # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    # In case not listed there, use "LicenseRef-<license-file-name>"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/CD3/BoostUnitDefinitions"
    # no "conan" and project name in topics. Use topics from the upstream listed on GH
    # Keep 'hearder-only' as topic
    topics = ("physical dimensions", "header-only")
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
        # export_conandata_patches(self)
        pass

    def layout(self):
        # src_folder must use the same source folder name the project
        basic_layout(self)

    def requirements(self):
        # prefer self.requires method instead of requires attribute
        # direct dependencies of header only libs are always transitive since they are included in public headers
        self.requires("boost/1.72.0", transitive_headers=True)

    # same package ID for any package
    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            # validate the minimum cpp standard supported when installing the package. For C++ projects only
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False
        )
        if (
            minimum_version
            and Version(self.settings.compiler.version) < minimum_version
        ):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        # download source package and extract to source folder
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    # not mandatory when there is no patch, but will suppress warning message about missing build() method
    def build(self):
        # The attribute no_copy_source should not be used when applying patches in build
        # apply_conandata_patches(self)
        pass

    # copy all files to the package folder
    def package(self):
        copy(
            self,
            pattern="LICENSE.md",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "src"),
        )

    def package_info(self):
        # folders not used for header-only
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # if package provides a CMake config file (package-config.cmake or packageConfig.cmake, with package::package target, usually installed in <prefix>/lib/cmake/<package>/)
        self.cpp_info.set_property("cmake_file_name", "BoostUnitDefinitions")
        self.cpp_info.set_property(
            "cmake_target_name", "BoostUnitDefinitions::BoostUnitDefinitions"
        )

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "BoostUnitDefinitions"
        self.cpp_info.filenames["cmake_find_package_multi"] = "BoostUnitDefinitions"
        self.cpp_info.names["cmake_find_package"] = "BoostUnitDefinitions"
        self.cpp_info.names["cmake_find_package_multi"] = "BoostUnitDefinitions"
