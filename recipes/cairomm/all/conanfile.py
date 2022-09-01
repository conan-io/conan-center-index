import glob
import os
import shutil

from conan import ConanFile
from conan.tools import (
    apple,
    build,
    files,
    microsoft,
    scm
)
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.gnu import PkgConfigDeps
from conan.errors import ConanInvalidConfiguration


class CairommConan(ConanFile):
    name = "cairomm"
    homepage = "https://github.com/freedesktop/cairomm"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-2.0"
    description = "cairomm is a C++ wrapper for the cairo graphics library."
    topics = ["cairo", "wrapper", "graphics"]

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "patches/**"
    short_paths = True

    @property
    def _abi_version(self):
        return "1.16" if scm.Version(self.version) >= "1.16.0" else "1.0"

    def validate(self):
        if hasattr(self, "settings_build") and build.cross_building(self):
            raise ConanInvalidConfiguration("Cross-building not implemented")
        if self.settings.compiler.get_safe("cppstd"):
            if self._abi_version == "1.16":
                build.check_min_cppstd(self, 17)
            else:
                build.check_min_cppstd(self, 11)
        if self.options.shared and not self.options["cairo"].shared:
            raise ConanInvalidConfiguration(
                "Linking against static cairo would cause shared cairomm to link "
                "against static glib which can cause problems."
            )

    def _patch_sources(self):
        files.apply_conandata_patches(self)
        if microsoft.is_msvc(self):
            # when using cpp_std=c++11 the /permissive- flag is added which
            # attempts enforcing standard conformant c++ code
            # the problem is that older versions of Windows SDK is not standard
            # conformant! see:
            # https://developercommunity.visualstudio.com/t/error-c2760-in-combaseapih-with-windows-sdk-81-and/185399
            files.replace_in_file(self,
                os.path.join(self._source_subfolder, "meson.build"),
                "cpp_std=c++", "cpp_std=vc++")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.shared:
            self.options["cairo"].shared = True

    def build_requirements(self):
        self.tool_requires("meson/0.63.1")
        self.tool_requires("pkgconf/1.7.4")

    def requirements(self):
        self.requires("cairo/1.17.4")

        if self._abi_version == "1.16":
            self.requires("libsigcpp/3.0.7")
        else:
            self.requires("libsigcpp/2.10.8")

    def layout(self):
        return basic_layout(self, src_folder="source_subfolder")

    def generate(self):
        deps = PkgConfigDeps(self)
        deps.generate()

        tc = MesonToolchain(self)
        tc.project_options.update({
            "build-examples": "false",
            "build-documentation": "false",
            "build-tests": "false",
            "msvc14x-parallel-installable": "false",
            "default_library": "shared" if self.options.shared else "static",
        })
        tc.generate()

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def build(self):
        self._patch_sources()
        meson = self._configure_meson()
        meson.build()

    def _configure_meson(self):
        meson = Meson(self)
        meson.configure()
        return meson

    def package(self):
        self.copy("COPYING", dst="licenses", src=self.source_folder)
        meson = self._configure_meson()
        meson.install()
        if microsoft.is_msvc(self):
            files.rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
            if not self.options.shared:
                files.rename(self,
                    os.path.join( self.package_folder, "lib", f"libcairomm-{self._abi_version}.a"),
                    os.path.join(self.package_folder, "lib", f"cairomm-{self._abi_version}.lib"),
                )

        for header_file in glob.glob(
                os.path.join(self.package_folder, "lib", f"cairomm-{self._abi_version}", "include", "*.h")):
            shutil.move(
                header_file,
                os.path.join(
                    self.package_folder,
                    "include",
                    f"cairomm-{self._abi_version}",
                    os.path.basename(header_file),
                ),
            )

        for dir_to_remove in ["pkgconfig", f"cairomm-{self._abi_version}"]:
            files.rmdir(self, os.path.join(self.package_folder, "lib", dir_to_remove))

    def package_info(self):
        cairomm_lib_name = f"cairomm-{self._abi_version}"
        self.cpp_info.components[cairomm_lib_name].set_property("pkg_config_name", cairomm_lib_name)
        self.cpp_info.components[cairomm_lib_name].includedirs = [os.path.join("include", cairomm_lib_name)]
        self.cpp_info.components[cairomm_lib_name].libs = [cairomm_lib_name]

        if apple.is_apple_os(self):
            self.cpp_info.components[cairomm_lib_name].frameworks = ["CoreFoundation"]

        if self._abi_version == "1.16":
            self.cpp_info.components[cairomm_lib_name].requires = ["libsigcpp::sigc++", "cairo::cairo_"]
        else:
            self.cpp_info.components[cairomm_lib_name].requires = ["libsigcpp::sigc++-2.0", "cairo::cairo_"]

    def package_id(self):
        if not self.options["cairo"].shared:
            self.info.requires["cairo"].full_package_mode()
