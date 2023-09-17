import glob
import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir, rename
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version


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

    @property
    def _compilers_minimum_version_17(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
        }

    @property
    def _abi_version(self):
        return "1.16" if Version(self.version) >= "1.16.0" else "1.0"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
            self.dependencies["cairo"].options.shared = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cairo/1.17.6")

        if self._abi_version == "1.16":
            self.requires("libsigcpp/3.0.7")
        else:
            self.requires("libsigcpp/2.10.8")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            if self._abi_version == "1.16":
                check_min_cppstd(self, 17)
            else:
                check_min_cppstd(self, 11)

        if not is_msvc(self) and self._abi_version == "1.16":
            minimum_version = self._compilers_minimum_version_17.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )

        if self.options.shared and not self.dependencies["cairo"].options.shared:
            raise ConanInvalidConfiguration(
                "Linking against static cairo would cause shared cairomm to link "
                "against static glib which can cause problems."
            )

    def build_requirements(self):
        self.tool_requires("meson/1.2.1")
        self.tool_requires("pkgconf/2.0.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options.update({
            "build-examples": "false",
            "build-documentation": "false",
            "build-tests": "false",
            "msvc14x-parallel-installable": "false",
            "default_library": "shared" if self.options.shared else "static",
        })
        tc.generate()

        PkgConfigDeps(self).generate()
        VirtualBuildEnv(self).generate()

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

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()

        if is_msvc(self):
            rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
            if not self.options.shared:
                rename(self,
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
            rmdir(self, os.path.join(self.package_folder, "lib", dir_to_remove))

        fix_apple_shared_install_name(self)

    def package_info(self):
        cairomm_lib_name = f"cairomm-{self._abi_version}"
        self.cpp_info.components[cairomm_lib_name].set_property("pkg_config_name", cairomm_lib_name)
        self.cpp_info.components[cairomm_lib_name].includedirs = [os.path.join("include", cairomm_lib_name)]
        self.cpp_info.components[cairomm_lib_name].libs = [cairomm_lib_name]
        self.cpp_info.components[cairomm_lib_name].requires = ["libsigcpp::libsigcpp", "cairo::cairo_"]

        if is_apple_os(self):
            self.cpp_info.components[cairomm_lib_name].frameworks = ["CoreFoundation"]


    def package_id(self):
        if not self.dependencies["cairo"].options.shared:
            self.info.requires["cairo"].full_package_mode()
