from conan import ConanFile
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import (
    get,
    rename,
    replace_in_file,
    rm,
    rmdir
)
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.errors import ConanInvalidConfiguration

import glob
import os
import shutil

required_conan_version = ">=1.54.0"


class LibSigCppConanV2(ConanFile):
    name = "libsigcpp"
    homepage = "https://github.com/libsigcplusplus/libsigcplusplus"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-3.0"
    description = "libsigc++ implements a typesafe callback system for standard C++."
    topics = ("libsigcpp", "callback")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    short_paths = True

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross-building not implemented")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def build_requirements(self):
        self.tool_requires("meson/0.63.3")
        self.tool_requires("pkgconf/1.9.3")

    def layout(self):
        basic_layout(self, src_folder="src")

    def generate(self):
        deps = PkgConfigDeps(self)
        deps.generate()

        tc = MesonToolchain(self)
        tc.project_options.update({
            "build-examples": "false",
            "build-documentation": "false",
            "default_library": "shared" if self.options.shared else "static"
        })
        tc.generate()

        env = VirtualBuildEnv(self)
        env.generate()

    def source(self):
        get(self,
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self.source_folder
        )

    def build(self):
        if not self.options.shared:
            replace_in_file(self,
                os.path.join(self.source_folder, "sigc++config.h.meson"),
                "define SIGC_DLL 1", "undef SIGC_DLL")
        replace_in_file(self, os.path.join(self.source_folder, "meson.build"), "subdir('tests')", "")
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self.source_folder)
        meson = Meson(self)
        meson.install()
        if self.settings.compiler == "Visual Studio":
            rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
            if not self.options.shared:
                rename(self,
                       os.path.join(self.package_folder, "lib", "libsigc-2.0.a"),
                       os.path.join(self.package_folder, "lib", "sigc-2.0.lib"))

        for header_file in glob.glob(os.path.join(self.package_folder, "lib", "sigc++-2.0", "include", "*.h")):
            shutil.move(
                header_file,
                os.path.join(self.package_folder, "include",
                             "sigc++-2.0", os.path.basename(header_file))
            )

        for dir_to_remove in ["pkgconfig", "sigc++-2.0"]:
            rmdir(self, os.path.join(self.package_folder, "lib", dir_to_remove))

    def package_info(self):
        self.cpp_info.components["sigc++-2.0"].set_property("pkg_config_name", "sigc++-2.0")
        self.cpp_info.components["sigc++-2.0"].includedirs.append(os.path.join("include", "sigc++-2.0"))
        self.cpp_info.components["sigc++-2.0"].libs = ["sigc-2.0"]
