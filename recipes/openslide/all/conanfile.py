import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain

required_conan_version = ">=1.53.0"


class OpenSlideConan(ConanFile):
    name = "openslide"
    description = "OpenSlide is a C library for reading whole slide image files (also known as virtual slides)"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://openslide.org/"
    topics = ("image", "pathology", "whole-slide-imaging", "slide-image",
              # supported formats
              "bif", "dicom", "dcm", "mrxs", "ndpi", "scn", "svs", "svslide", "tiff", "vms", "vmu")

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cairo/1.18.0")
        self.requires("gdk-pixbuf/2.42.10")
        self.requires("glib/2.78.1", force=True)  # FIXME
        self.requires("libdicom/1.0.5")
        self.requires("libjpeg/9e")
        self.requires("libpng/1.6.40")
        self.requires("libtiff/4.6.0")
        self.requires("libxml2/2.11.5")
        self.requires("openjpeg/2.5.0")
        self.requires("sqlite3/3.44.0")
        self.requires("zlib/[>=1.2.11 <2]")

    def build_requirements(self):
        self.tool_requires("meson/1.2.3")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")
        self.tool_requires("glib/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()
        tc = MesonToolchain(self)
        tc.project_options["test"] = "disabled"
        tc.project_options["doc"] = "disabled"
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING.LESSER", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["openslide"]
        self.cpp_info.includedirs.append(os.path.join("include", "openslide"))
