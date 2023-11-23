import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, chdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.54.0"


class PackageConan(ConanFile):
    name = "libecwj2"
    description = "Legacy version of the ERDAS ECW/JP2 SDK. Provides support for the ECW (Enhanced Compressed Wavelet) and the JPEG 2000 image formats."
    license = "DocumentRef-License.txt:LicenseRef-libecwj2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://trac.osgeo.org/gdal/wiki/ECW"
    topics = ("image", "ecw", "jp2", "jpeg2000")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=os.path.join(self.export_sources_folder, "src", "Source"))
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libjpeg/9e")
        self.requires("tinyxml/2.6.2", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 98)
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("Only Linux and FreeBSD are currently supported. Contributions are welcome.")

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._chmod_plus_x(os.path.join(self.source_folder, "configure"))

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        rmdir(self, os.path.join(self.source_folder, "Source", "C", "libjpeg"))
        rmdir(self, os.path.join(self.source_folder, "Source", "C", "tinyxml"))
        replace_in_file(self, os.path.join(self.source_folder, "configure.in"), " -fpic", "")

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "License.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "lib"), os.path.join(self.package_folder, "lib"))
        copy(self, "*", os.path.join(self.source_folder, "Source", "include"), os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["ecwj2"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "rt", "m", "pthread"])
        if stdcpp_library(self):
            self.cpp_info.system_libs.append(stdcpp_library(self))
