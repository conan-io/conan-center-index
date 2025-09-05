from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os

required_conan_version = ">=2.0"


class PackageConan(ConanFile):
    name = "capypdf"
    description = "Fully color-managed PDF generation library"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jpakkane/capypdf"
    topics = ("pdf", "rendering")
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

    def configure(self):
       self.options["libtiff/*"].jpeg = 'libjpeg-turbo'

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libpng/[>=1.6 <2]")
        self.requires("lcms/2.16")
        self.requires("freetype/2.13.2")
        self.requires("libtiff/4.7.0")

    def build_requirements(self):
        self.build_requires("meson/1.7.2")
        self.build_requires("pkgconf/2.2.0")

    def validate(self):
        check_min_cppstd(self, 23)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["capypdf"]
        self.cpp_info.includedirs = ['include/capypdf-0']
        self.cpp_info.set_property("pkg_config_name", "capypdf")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m"])
