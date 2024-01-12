from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "libvdpau"
    description = "Video Decode and Presentation API for UNIX"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freedesktop.org/wiki/Software/VDPAU/"
    topics = ("video", "decode", "presentation")
    package_type = "shared-library"
    provides = "vdpau"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_dri2": [True, False],
    }
    default_options = {
        "with_dri2": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("xorg/system")

    def build_requirements(self):
        self.tool_requires("meson/1.3.1")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["dri2"] = "true" if self.options.with_dri2 else "false"
        tc.project_options["documentation"] = "false"
        tc.project_options["sysconfdir"] = "share"
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["vdpau"]
        self.cpp_info.set_property("pkg_config_name", "vdpau")
        self.cpp_info.system_libs.extend(["pthread", "dl"])
