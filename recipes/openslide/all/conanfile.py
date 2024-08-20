import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc

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
        "jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "jpeg": "libjpeg",
    }

    def export_sources(self):
        export_conandata_patches(self)

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
        self.requires("glib/2.78.3")
        self.requires("libdicom/1.0.5")
        self.requires("libpng/[>=1.6 <2]")
        self.requires("libtiff/4.6.0")
        self.requires("libxml2/[>=2.12.5 <3]")
        self.requires("openjpeg/2.5.2")
        self.requires("sqlite3/3.45.3")
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.2")
        elif self.options.jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.5")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("OpenSlide requires GNU C extensions support and is not compatible with MSVC")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.2.3 <2]")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
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
        apply_conandata_patches(self)
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

        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreText"]

        self.cpp_info.requires = [
            "cairo::cairo_",
            "gdk-pixbuf::gdk-pixbuf",
            "glib::gio-2.0",
            "glib::glib-2.0",
            "glib::gobject-2.0",
            "libdicom::libdicom",
            "libpng::libpng",
            "libtiff::libtiff",
            "libxml2::libxml2",
            "openjpeg::openjpeg",
            "sqlite3::sqlite3",
            "zlib::zlib",
        ]
        if self.options.jpeg == "libjpeg":
            self.cpp_info.requires.append("libjpeg::libjpeg")
        elif self.options.jpeg == "libjpeg-turbo":
            self.cpp_info.requires.append("libjpeg-turbo::jpeg")
        elif self.options.jpeg == "mozjpeg":
            self.cpp_info.requires.append("mozjpeg::libjpeg")
