from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rm, rmdir, chdir, rename, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
import glob
import os


required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "openslide"
    description = "OpenSlide is a C library for reading whole slide image files (also known as virtual slides)."
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/openslide/openslide"
    topics = ("image", "image-processing")
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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self) and not self.options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} cannot be built statically for msvc"
            )

    def requirements(self):
        self.requires("libjpeg/9e")
        self.requires("libpng/1.6.39")
        self.requires("glib/2.76.1")
        self.requires("libtiff/4.4.0")
        self.requires("libxml2/2.9.14")
        self.requires("sqlite3/3.39.4")
        self.requires("zlib/1.2.13")
        self.requires("openjpeg/2.5.0")
        self.requires("cairo/1.17.2")
        self.requires("gdk-pixbuf/2.42.10")

    def build_requirements(self):
        self.tool_requires("meson/1.0.0")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["doc"] = "disabled"
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate()
        ms = VirtualRunEnv(self)
        ms.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def _fix_library_names(self, path):
        # https://github.com/mesonbuild/meson/issues/1412
        if not self.options.shared and is_msvc(self):
            with chdir(self, path):
                for filename_old in glob.glob("*.a"):
                    filename_new = filename_old[3:-2] + ".lib"
                    self.output.info(f"rename {filename_old} into {filename_new}")
                    rename(self, filename_old, filename_new)

    def package(self):
        copy(self, pattern="COPYING.LESSER", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

        self._fix_library_names(os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.includedirs = ["include", "include/openslide"]
        self.cpp_info.libs = ["openslide"]
        self.cpp_info.set_property("pkg_config_name", "openslide")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
