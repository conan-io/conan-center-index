import glob
import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name, is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rename, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class CairommConan(ConanFile):
    name = "cairomm"
    description = "cairomm is a C++ wrapper for the cairo graphics library."
    license = "LGPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.cairographics.org/cairomm/"
    topics = ["cairo", "wrapper", "graphics"]
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _abi_version(self):
        return "1.16" if Version(self.version) >= "1.16.0" else "1.0"

    @property
    def _min_cppstd(self):
        return 17 if self._abi_version == "1.16" else 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.shared:
            self.options["cairo"].shared = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cairo/1.18.0", transitive_headers=True, transitive_libs=True)
        self.requires("fontconfig/2.14.2", transitive_headers=True, transitive_libs=True)
        if self._abi_version == "1.16":
            self.requires("libsigcpp/3.0.7", transitive_headers=True, transitive_libs=True)
        else:
            self.requires("libsigcpp/2.10.8", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross-building not implemented")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if self.options.shared and not self.dependencies["cairo"].options.shared:
            raise ConanInvalidConfiguration(
                "Linking against static cairo would cause shared cairomm to link "
                "against static glib which can cause problems."
            )

    def build_requirements(self):
        self.tool_requires("meson/1.2.3")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = MesonToolchain(self)
        tc.project_options = {
            "build-examples": "false",
            "build-documentation": "false",
            "build-tests": "false",
            "msvc14x-parallel-installable": "false",
            "default_library": "shared" if self.options.shared else "static",
            "libdir": "lib",
        }
        if not self.options.shared:
            tc.preprocessor_definitions["CAIROMM_STATIC_LIB"] = "1"
        tc.generate()

    def _patch_sources(self):
        if is_msvc(self):
            # when using cpp_std=c++11 the /permissive- flag is added which
            # attempts enforcing standard conformant c++ code
            # the problem is that older versions of Windows SDK is not standard
            # conformant! see:
            # https://developercommunity.visualstudio.com/t/error-c2760-in-combaseapih-with-windows-sdk-81-and/185399
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                            "cpp_std=c++",
                            "cpp_std=vc++")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()
        if is_msvc(self):
            rm(self, "*.pdb", os.path.join(self.package_folder, "bin"), recursive=True)
            if not self.options.shared:
                rename(self,
                    os.path.join(self.package_folder, "lib", f"libcairomm-{self._abi_version}.a"),
                    os.path.join(self.package_folder, "lib", f"cairomm-{self._abi_version}.lib"))

        for header_file in glob.glob(
            os.path.join(self.package_folder, "lib", f"cairomm-{self._abi_version}", "include", "*.h")
        ):
            shutil.move(
                header_file,
                os.path.join(self.package_folder, "include", f"cairomm-{self._abi_version}", os.path.basename(header_file)),
            )

        for dir_to_remove in ["pkgconfig", f"cairomm-{self._abi_version}"]:
            rmdir(self, os.path.join(self.package_folder, "lib", dir_to_remove))

        fix_apple_shared_install_name(self)

    def package_info(self):
        name = f"cairomm-{self._abi_version}"
        self.cpp_info.components[name].set_property("pkg_config_name", name)
        self.cpp_info.components[name].includedirs = [os.path.join("include", name)]
        self.cpp_info.components[name].libs = [name]
        self.cpp_info.components[name].requires = ["libsigcpp::libsigcpp", "cairo::cairo", "fontconfig::fontconfig"]
        if not self.options.shared:
            self.cpp_info.components[name].defines = ["CAIROMM_STATIC_LIB"]
        if is_apple_os(self):
            self.cpp_info.components[name].frameworks = ["CoreFoundation"]
