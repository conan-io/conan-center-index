from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building, check_min_cppstd
from conan.tools.files import rename, apply_conandata_patches, replace_in_file, get, copy, rm, rmdir, export_conandata_patches
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration
from conan.tools.scm import Version

import glob
import os
import shutil


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

    short_paths = True

    def _abi_version(self):
        return "1.16" if Version(self.version) >= "1.16.0" else "1.0"

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross-building not implemented")
        if self.settings.compiler.get_safe("cppstd"):
            if self._abi_version() == "1.16":
                check_min_cppstd(self, 17)
            else:
                check_min_cppstd(self, 11)
        if self.options.shared and not self.options["cairo"].shared:
            raise ConanInvalidConfiguration(
                "Linking against static cairo would cause shared cairomm to link "
                "against static glib which can cause problems."
            )

    def _patch_sources(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            # when using cpp_std=c++11 the /permissive- flag is added which
            # attempts enforcing standard conformant c++ code
            # the problem is that older versions of Windows SDK is not standard
            # conformant! see:
            # https://developercommunity.visualstudio.com/t/error-c2760-in-combaseapih-with-windows-sdk-81-and/185399
            replace_in_file(self,
                os.path.join(self.source_folder, "meson.build"),
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
        self.build_requires("meson/1.0.0")
        self.build_requires("pkgconf/1.9.3")

    def requirements(self):
        self.requires("cairo/1.17.6")

        if self._abi_version() == "1.16":
            self.requires("libsigcpp/3.0.7")
        else:
            self.requires("libsigcpp/2.10.8")

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self,
            **self.conan_data["sources"][self.version],
            strip_root=True
        )

    def layout(self):
        basic_layout(self, src_folder="src")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def generate(self):
        PkgConfigDeps(self).generate()

        tc = MesonToolchain(self)
        tc.project_options.update({
            "build-examples": "false",
            "build-documentation": "false",
            "build-tests": "false",
            "msvc14x-parallel-installable": "false",
            "default_library": "shared" if self.options.shared else "static",
        })
        tc.generate()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        if is_msvc(self):
            rm(self, "*.pdb",os.path.join(self.package_folder, "bin"), recursive=True)
            if not self.options.shared:
                rename(
                    self,
                    os.path.join(
                        self.package_folder,
                        "lib",
                        f"libcairomm-{self._abi_version()}.a",
                    ),
                    os.path.join(self.package_folder, "lib",
                                 f"cairomm-{self._abi_version()}.lib"),
                )

        for header_file in glob.glob(
                os.path.join(
                    self.package_folder,
                    "lib",
                    f"cairomm-{self._abi_version()}",
                    "include",
                    "*.h",
                )):
            shutil.move(
                header_file,
                os.path.join(
                    self.package_folder,
                    "include",
                    f"cairomm-{self._abi_version()}",
                    os.path.basename(header_file),
                ),
            )

        for dir_to_remove in ["pkgconfig", f"cairomm-{self._abi_version()}"]:
            rmdir(self, os.path.join(self.package_folder, "lib",
                                     dir_to_remove))

    def package_info(self):
        if self._abi_version() == "1.16":
            self.cpp_info.components["cairomm-1.16"].names[
                "pkg_config"] = "cairomm-1.16"
            self.cpp_info.components["cairomm-1.16"].includedirs = [
                os.path.join("include", "cairomm-1.16")
            ]
            self.cpp_info.components["cairomm-1.16"].libs = ["cairomm-1.16"]
            self.cpp_info.components["cairomm-1.16"].requires = [
                "libsigcpp::sigc++", "cairo::cairo_"
            ]
            if is_apple_os(self):
                self.cpp_info.components["cairomm-1.16"].frameworks = [
                    "CoreFoundation"
                ]
        else:
            self.cpp_info.components["cairomm-1.0"].names[
                "pkg_config"] = "cairomm-1.0"
            self.cpp_info.components["cairomm-1.0"].includedirs = [
                os.path.join("include", "cairomm-1.0")
            ]
            self.cpp_info.components["cairomm-1.0"].libs = ["cairomm-1.0"]
            self.cpp_info.components["cairomm-1.0"].requires = [
                "libsigcpp::sigc++-2.0", "cairo::cairo_"
            ]
            if is_apple_os(self):
                self.cpp_info.components["cairomm-1.0"].frameworks = [
                    "CoreFoundation"
                ]

    def package_id(self):
        self.info.requires["cairo"].full_package_mode()
