from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os

required_conan_version = ">=1.53.0"


class LibseatConan(ConanFile):
    name = "libseat"
    description = ("A minimal seat management daemon, and a universal seat management library")
    topics = ("login", "session", "seat", "seatd")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sr.ht/~kennylevinsen/seatd/"
    license = "MIT"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "builtin": [True, False],
        "defaultpath": [None, "ANY"],
        "logind": [False, "elogind", "systemd"],
        "seatd": [True, False],
        "server": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "defaultpath": None,
        "builtin": False,
        "logind": False,
        "seatd": True,
        "server": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.logind == "systemd":
            self.requires("libsystemd/253.10")

    def validate(self):
        if not self.settings.os in ["FreeBSD", "Linux"]:
            raise ConanInvalidConfiguration(f"{self.ref} only supports FreeBSD and Linux")
        if self.options.logind == "elogind":
            raise ConanInvalidConfiguration(f"{self.ref} may not be built with elogind support since there is no elogind Conan package yet")

    def build_requirements(self):
        self.tool_requires("meson/1.2.2")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options["libseat-builtin"] = "enabled" if self.options.builtin else "disabled"
        tc.project_options["libseat-logind"] = str(self.options.logind) if self.options.logind else "disabled"
        tc.project_options["libseat-seatd"] = "enabled" if self.options.seatd else "disabled"
        tc.project_options["server"] = "enabled" if self.options.server else "disabled"
        tc.project_options["examples"] = "disabled"
        tc.project_options["man-pages"] = "disabled"
        tc.project_options["defaultpath"] = "" if self.options.defaultpath is None else str(self.options.defaultpath)
        tc.c_args.append("-Wno-error")
        tc.generate()
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()
        env = VirtualBuildEnv(self)
        env.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        pkg_config_dir = os.path.join(self.package_folder, "lib", "pkgconfig")
        rmdir(self, pkg_config_dir)

    def package_info(self):
        self.cpp_info.libs = ["seat"]
        self.cpp_info.system_libs.append("rt")
        pkgconfig_variables = {
            "have_builtin": self.options.builtin,
            "have_logind": "true" if self.options.logind else "false",
            "have_seatd": self.options.seatd,
        }
        self.cpp_info.set_property(
            "pkg_config_custom_content",
            "\n".join(f"{key}={value}" for key,value in pkgconfig_variables.items()))
