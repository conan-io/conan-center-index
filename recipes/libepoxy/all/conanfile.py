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


class EpoxyConan(ConanFile):
    name = "libepoxy"
    description = "libepoxy is a library for handling OpenGL function pointer management"
    topics = ("opengl",)
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/anholt/libepoxy"
    license = "MIT"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "glx": [True, False],
        "egl": [True, False],
        "x11": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "glx": True,
        "egl": True,
        "x11": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            self.options.shared = True
        if self.settings.os not in ["FreeBSD", "Linux"]:
            del self.options.glx
            del self.options.egl
            del self.options.x11

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        if self.settings.os in ["FreeBSD", "Linux"]:
            if self.options.get_safe("egl"):
                self.options["libglvnd"].egl = True
            if self.options.get_safe("glx"):
                self.options["libglvnd"].glx = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # epoxy/egl_generated.h includes EGL/eglplatform.h
        if self.settings.os in ["FreeBSD", "Linux"]:
            if self.options.get_safe("egl") or self.options.get_safe("glx"):
                self.requires("libglvnd/1.7.0", transitive_headers=bool(self.options.get_safe("egl")))
            if self.options.get_safe("x11"):
                self.requires("xorg/system")
        else:
            self.requires("opengl/system")

    def validate(self):
        if self.settings.os == "Windows" and not self.options.shared:
            raise ConanInvalidConfiguration("Static builds on Windows are not supported")
        if self.settings.os in ["FreeBSD", "Linux"] and self.options.glx and not self.options.x11:
            raise ConanInvalidConfiguration(f"{self.ref} requires the x11 option to be enabled when the glx option is enabled")
        if self.settings.os in ["FreeBSD", "Linux"] and self.options.get_safe("egl") and not self.dependencies["libglvnd"].options.egl:
            raise ConanInvalidConfiguration(f"{self.ref} requires the egl option of libglvnd to be enabled")
        if self.settings.os in ["FreeBSD", "Linux"] and self.options.get_safe("glx") and not self.dependencies["libglvnd"].options.glx:
            raise ConanInvalidConfiguration(f"{self.ref} requires the glx option of libglvnd to be enabled")


    def build_requirements(self):
        self.tool_requires("meson/1.4.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = MesonToolchain(self)
        tc.project_options["docs"] = "false"
        tc.project_options["tests"] = "false"
        for opt in ["glx", "egl"]:
            tc.project_options[opt] = "yes" if self.options.get_safe(opt, False) else "no"
        for opt in ["x11"]:
            tc.project_options[opt] = "true" if self.options.get_safe(opt, False) else "false"
        tc.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["epoxy"]
        if self.settings.os in ["FreeBSD", "Linux"]:
            self.cpp_info.system_libs = ["dl"]
        self.cpp_info.set_property("pkg_config_name", "epoxy")
        pkgconfig_variables = {
            'epoxy_has_glx': '1' if self.options.get_safe("glx") else '0',
            'epoxy_has_egl': '1' if self.options.get_safe("egl") else '0',
            'epoxy_has_wgl': '1' if self.settings.os == "Windows" else '0',
        }
        self.cpp_info.set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key,value in pkgconfig_variables.items()),
        )
