from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.52.0"


class ChefFunConan(ConanFile):
    name = "chef-fun"
    homepage = "https://gitlab.com/libchef/chef-fun"
    description = "C++ Functional programming support library"
    topics = ("functional programming", "cpp", "library" )
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    settings = "os", "arch", "compiler", "build_type"
    # Keep these or explain why it's not required for this particular case
    # Do not copy sources to build folder for header only projects, unless you need to apply patches
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 20

    # In case the project requires C++14/17/20/... the minimum compiler version should be listed
    # Not tested on "msvc", "clang", and "apple-clang". Possibly it works there
    # given a sufficient recent version
    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9.4.0",
        }

    # Use the export_sources(self) method instead of the exports_sources attribute.
    # This allows finer grain exportation of patches per version
    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        # src_folder must use the same source folder name than the project
        basic_layout(self, src_folder="src")

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

#    def requirements(self):
#        # Prefer self.requires method instead of requires attribute
#        # Direct dependencies of header only libs are always transitive since they are included in public headers
#        self.requires("dependency/0.8.1", transitive_headers=True)

    def source(self):
        # Download source package and extract to source folder
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    # Not mandatory when there is no patch, but will suppress warning message about missing build() method
    def build(self):
        # The attribute no_copy_source should not be used when applying patches in build
        apply_conandata_patches(self)

    # Copy all files to the package folder
    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hh",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )
        copy(
            self,
            pattern="*.tcc",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        # Folders not used for header-only
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # Set these to the appropriate values if the package has an official FindPACKAGE.cmake
        # listed in https://cmake.org/cmake/help/latest/manual/cmake-modules.7.html#find-modules
        # examples: bzip2, freetype, gdal, icu, libcurl, libjpeg, libpng, libtiff, openssl, sqlite3, zlib...
        self.cpp_info.set_property("cmake_module_file_name", "ChefFun")
        self.cpp_info.set_property("cmake_module_target_name", "ChefFun::ChefFun")
        # Set these to the appropriate values if package provides a CMake config file
        # (package-config.cmake or packageConfig.cmake, with package::package target, usually installed in <prefix>/lib/cmake/<package>/)
        self.cpp_info.set_property("cmake_file_name", "chef-fun")
        self.cpp_info.set_property("cmake_target_name", "chef-fun::chef-fun")
        # Set this to the appropriate value if the package provides a pkgconfig file
        # (package.pc, usually installed in <prefix>/lib/pkgconfig/)
        self.cpp_info.set_property("pkg_config_name", "chef-fun")

        ## Add m, pthread and dl if needed in Linux/FreeBSD
        #if self.settings.os in ["Linux", "FreeBSD"]:
        #    self.cpp_info.system_libs.extend(["dl", "m", "pthread"])

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "chef-fun"
        self.cpp_info.names["cmake_find_package_multi"] = "chef-fun"
        self.cpp_info.filenames["cmake_find_package"] = "chef-fun"
        self.cpp_info.filenames["cmake_find_package_multi"] = "chef-fun"
