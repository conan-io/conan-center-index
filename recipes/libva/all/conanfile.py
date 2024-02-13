from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os


required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "libva"
    description = "Libva is an implementation for VA-API"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/intel/libva"
    topics = ("VA-API", "Video", "Acceleration")
    provides = "vaapi"
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_drm": [True, False],
        "with_x11": [True, False],
        "with_glx": [True, False],
        "with_wayland": [True, False],
        "with_win32": [True, False],
    }
    default_options = {
        "with_drm": True,
        "with_x11": True,
        "with_glx": True,
        "with_wayland": True,
        "with_win32": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os != "Windows":
            del self.options.with_win32

        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_x11
            del self.options.with_glx
            del self.options.with_drm

        if self.settings.os != "Linux":
            del self.options.with_wayland

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_x11"):
            self.requires("xorg/system")
        if self.options.get_safe("with_drm"):
            self.requires("libdrm/2.4.119")
        if self.options.get_safe("with_wayland"):
            self.requires("wayland/1.22.0")
        if self.options.get_safe("with_glx"):
            self.requires("opengl/system")

    def validate(self):
        if self.options.get_safe("with_glx") and not self.options.get_safe("with_x11"):
            raise ConanInvalidConfiguration(f"{self.ref} requires x11 when glx is enabled")
        if not self.options.get_safe("with_drm") and not self.options.get_safe("with_x11") and not self.options.get_safe("with_wayland") and not self.options.get_safe("with_win32"):
            raise ConanInvalidConfiguration(f"{self.ref} can not be built without at least one backend dev files.")

    def build_requirements(self):
        if self.options.get_safe("with_wayland"):
            self.tool_requires("wayland/1.22.0")
        self.tool_requires("meson/1.3.1")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["disable_drm"] = not self.options.get_safe("with_drm")
        for opt in ['with_x11', 'with_glx', 'with_wayland', 'with_win32']:
            tc.project_options[opt] = "yes" if self.options.get_safe(opt) else "no"
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
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

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.components["libva_"].libs = ["va"]
        self.cpp_info.components["libva_"].set_property("pkg_config_name", "libva")

        if self.options.get_safe("with_drm"):
            self.cpp_info.components["libva-drm"].libs = ["va-drm"]
            self.cpp_info.components["libva-drm"].set_property("pkg_config_name", "libva-drm")
            self.cpp_info.components["libva-drm"].requires = ["libva_", "libdrm::libdrm"]

        if self.options.get_safe("with_x11"):
            self.cpp_info.components["libva-x11"].libs = ["va-x11"]
            self.cpp_info.components["libva-x11"].set_property("pkg_config_name", "libva-x11")
            self.cpp_info.components["libva-x11"].requires = ["libva_", "xorg::xorg"]

        if self.options.get_safe("with_glx"):
            self.cpp_info.components["libva-glx"].libs = ["va-glx"]
            self.cpp_info.components["libva-glx"].set_property("pkg_config_name", "libva-glx")
            self.cpp_info.components["libva-glx"].requires = ["libva_", "opengl::opengl"]

        if self.options.get_safe("with_wayland"):
            self.cpp_info.components["libva-wayland"].libs = ["va-wayland"]
            self.cpp_info.components["libva-wayland"].set_property("pkg_config_name", "libva-wayland")
            self.cpp_info.components["libva-wayland"].requires = ["libva_", "wayland::wayland-client"]

        if self.options.get_safe("with_win32"):
            self.cpp_info.components["libva-win32"].libs = ["va_win32"]
            self.cpp_info.components["libva-win32"].set_property("pkg_config_name", "libva-win32")
            self.cpp_info.components["libva-win32"].requires = ["libva_"]
