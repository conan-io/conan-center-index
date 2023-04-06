from conan import ConanFile
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    rename,
    replace_in_file,
    rm,
    rmdir
)
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conan.tools.env import VirtualBuildEnv
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.gnu import PkgConfigDeps

import os

required_conan_version = ">=1.53.0"


class FontconfigConan(ConanFile):
    name = "fontconfig"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Fontconfig is a library for configuring and customizing font access"
    homepage = "https://gitlab.freedesktop.org/fontconfig/fontconfig"
    topics = ("fonts", "freedesktop")
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

    def requirements(self):
        self.requires("freetype/2.13.0")
        self.requires("expat/2.5.0")
        if self.settings.os == "Linux":
            self.requires("libuuid/1.0.3")

    def build_requirements(self):
        self.tool_requires("gperf/3.1")
        self.tool_requires("meson/1.0.1")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        deps = PkgConfigDeps(self)
        deps.generate()

        tc = MesonToolchain(self)
        tc.project_options.update({
            "doc": "disabled",
            "nls": "disabled",
            "tests": "disabled",
            "tools": "disabled"
        })
        tc.generate()

        env = VirtualBuildEnv(self)
        env.generate()

    def _patch_files(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                        "freetype_req = '>= 21.0.15'",
                        f"freetype_req = '{Version(self.dependencies['freetype'].ref.version)}'")

    def build(self):
        self._patch_files()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        meson = Meson(self)
        meson.install()
        if is_msvc(self):
            if os.path.isfile(os.path.join(self.package_folder, "lib", "libfontconfig.a")):
                rename(self, os.path.join(self.package_folder, "lib", "libfontconfig.a"),
                         os.path.join(self.package_folder, "lib", "fontconfig.lib"))

        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rm(self, "*.conf", os.path.join(self.package_folder, "bin", "etc", "fonts", "conf.d"))
        rm(self, "*.def", os.path.join(self.package_folder, "lib"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Fontconfig")
        self.cpp_info.set_property("cmake_target_name", "Fontconfig::Fontconfig")
        self.cpp_info.set_property("pkg_config_name", "fontconfig")
        self.cpp_info.libs = ["fontconfig"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["m", "pthread"])

        self.cpp_info.names["cmake_find_package"] = "Fontconfig"
        self.cpp_info.names["cmake_find_package_multi"] = "Fontconfig"

        fontconfig_file = os.path.join(self.package_folder, "bin", "etc", "fonts", "fonts.conf")
        self.output.info(f"Creating FONTCONFIG_FILE environment variable: {fontconfig_file}")
        self.runenv_info.prepend_path("FONTCONFIG_FILE", fontconfig_file)
        self.env_info.FONTCONFIG_FILE = fontconfig_file # TODO: remove in conan v2?

        fontconfig_path = os.path.join(self.package_folder, "bin", "etc", "fonts")
        self.output.info(f"Creating FONTCONFIG_PATH environment variable: {fontconfig_path}")
        self.runenv_info.prepend_path("FONTCONFIG_PATH", fontconfig_path)
        self.env_info.FONTCONFIG_PATH = fontconfig_path # TODO: remove in conan v2?
