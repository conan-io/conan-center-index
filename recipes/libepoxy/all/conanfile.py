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
        if self.settings.os != "Linux":
            del self.options.glx
            del self.options.egl
            del self.options.x11

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opengl/system")
        if self.settings.os == "Linux":
            if self.options.x11:
                self.requires("xorg/system")
            if self.options.egl:
                self.requires("egl/system")

    def validate(self):
        if self.settings.os == "Windows" and not self.options.shared:
            raise ConanInvalidConfiguration("Static builds on Windows are not supported")

    def build_requirements(self):
        self.tool_requires("meson/1.3.1")

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
        if self.settings.os == "Linux":
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
