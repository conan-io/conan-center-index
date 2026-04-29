import os

from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, rm, rmdir, get
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.microsoft import is_msvc
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=2.0.9"

class Librdata(ConanFile):
    name = "librdata"
    description = "librdata is a library for read and write R data frames from C"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/WizardMac/librdata"
    topics = ("r", "rdata", "rds", "data-frames")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("bzip2/1.0.8")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("xz_utils/[>=5.4.5 <6]")
        if is_msvc(self):
            self.requires("libiconv/1.18")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        # INFO: gettext is required by libtool due macro: AM_ICONV
        self.tool_requires("gettext/0.22.5")
        if is_msvc(self):
            self.tool_requires("cmake/[>=3.22 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)

    def generate(self):
        self._patch_sources()
        if is_msvc(self):
            tc = CMakeToolchain(self)
            tc.generate()
            tc = CMakeDeps(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()
            dep = AutotoolsDeps(self)
            dep.generate()

    def build(self):
        if is_msvc(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if is_msvc(self):
            cmake = CMake(self)
            cmake.install()
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["rdata"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("m")
