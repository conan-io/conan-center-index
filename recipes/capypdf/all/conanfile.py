from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.0.9"


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
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["libtiff"].jpeg = "libjpeg-turbo"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libjpeg-turbo/[>=3.0.0 <4]")
        self.requires("libpng/[>=1.6 <2]")
        self.requires("lcms/[>=2.16 <3]")
        self.requires("freetype/2.13.2")
        self.requires("libtiff/[>=4.6.0 <5]")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2.0 <3]")

    def validate(self):
        check_min_cppstd(self, 23)
        if self.dependencies["libtiff"].options.get_safe("jpeg") != "libjpeg-turbo":
            raise ConanInvalidConfiguration("capypdf requires libtiff built with JPEG support")

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
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        folders = os.listdir(os.path.join(self.package_folder, "lib",))
        python_folder = [f for f in folders if f.startswith("python") and os.path.isdir(os.path.join(self.package_folder, "lib", f))]
        if python_folder:
            rmdir(self, os.path.join(self.package_folder, "lib", python_folder[0]))
        rmdir(self, os.path.join(self.package_folder, "lib", "site-packages"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["capypdf"]
        self.cpp_info.includedirs = ['include', 'include/capypdf-0']
        self.cpp_info.set_property("pkg_config_name", "capypdf")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m"])
