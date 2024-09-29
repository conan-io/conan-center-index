from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.52.0"


class PackageConan(ConanFile):
    name = "qoi"
    description = "The “Quite OK Image Format” for fast, lossless image compression"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://qoiformat.org/"
    topics = ("image", "compression", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    # same package ID for any package
    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    # Not mandatory when there is no patch, but will suppress warning message about missing build() method
    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(
            self,
            "*.h",
            self.source_folder,
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        # Folders not used for header-only
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # # Set these to the appropriate values if the package has an official FindPACKAGE.cmake
        # # listed in https://cmake.org/cmake/help/latest/manual/cmake-modules.7.html#find-modules
        # # examples: bzip2, freetype, gdal, icu, libcurl, libjpeg, libpng, libtiff, openssl, sqlite3, zlib...
        # self.cpp_info.set_property("cmake_module_file_name", "PACKAGE")
        # self.cpp_info.set_property("cmake_module_target_name", "PACKAGE::PACKAGE")
        # # Set these to the appropriate values if package provides a CMake config file
        # # (package-config.cmake or packageConfig.cmake, with package::package target, usually installed in <prefix>/lib/cmake/<package>/)
        # self.cpp_info.set_property("cmake_file_name", "package")
        # self.cpp_info.set_property("cmake_target_name", "package::package")
        # # Set this to the appropriate value if the package provides a pkgconfig file
        # # (package.pc, usually installed in <prefix>/lib/pkgconfig/)
        # self.cpp_info.set_property("pkg_config_name", "package")

        # # Add m, pthread and dl if needed in Linux/FreeBSD
        # if self.settings.os in ["Linux", "FreeBSD"]:
        #     self.cpp_info.system_libs.extend(["dl", "m", "pthread"])

        # # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        # self.cpp_info.filenames["cmake_find_package"] = "PACKAGE"
        # self.cpp_info.filenames["cmake_find_package_multi"] = "package"
        # self.cpp_info.names["cmake_find_package"] = "PACKAGE"
        # self.cpp_info.names["cmake_find_package_multi"] = "package"
