from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os


required_conan_version = ">=1.53.0"


class BasuConan(ConanFile):
    name = "basu"
    description = "The sd-bus library, extracted from systemd"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git.sr.ht/~emersion/basu"
    topics = ("dbus", "sd-bus", "systemd")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libcap": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libcap": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.with_libcap

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_libcap"):
            self.requires("libcap/2.69")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration(
                f"{self.ref} does not support {self.settings.os}")

    def build_requirements(self):
        self.tool_requires("meson/1.3.2")
        self.tool_requires("gperf/3.1")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        feature = lambda option: "enabled" if option else "disabled"

        tc = MesonToolchain(self)
        tc.project_options["auto_features"] = "disabled"
        tc.project_options["libcap"] = feature(self.options.get_safe("with_libcap"))
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
        copy(self, "LICENSE.LGPL2.1", self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["basu"]
        self.cpp_info.set_property("pkg_config_name", "basu")
        self.cpp_info.system_libs.extend(["m", "pthread", "rt"])
