import os
import glob
import shutil

from conan import ConanFile, conan_version
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    replace_in_file,
    rename,
    rm,
    rmdir
)
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class GlibmmConan(ConanFile):
    name = "glibmm"
    homepage = "https://gitlab.gnome.org/GNOME/glibmm"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    description = "glibmm is a C++ API for parts of glib that are useful for C++."
    topics = ("giomm",)
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
    short_paths = True

    @property
    def _abi_version(self):
        return "2.68" if Version(self.version) >= "2.68.0" else "2.4"

    @property
    def _glibmm_lib(self):
        return f"glibmm-{self._abi_version}"

    @property
    def _giomm_lib(self):
        return f"giomm-{self._abi_version}"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.shared:
            wildcard = "" if Version(conan_version) < "2.0.0" else "/*"
            self.options[f"glib{wildcard}"].shared = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glib/2.76.2")
        if self._abi_version == "2.68":
            self.requires("libsigcpp/3.0.7")
        else:
            self.requires("libsigcpp/3.0.7")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            if self._abi_version == "2.68":
                check_min_cppstd(self, 17)
            else:
                check_min_cppstd(self, 11)

        if self.options.shared and not self.dependencies["glib"].options.shared:
            raise ConanInvalidConfiguration(
                "Linking a shared library against static glib can cause unexpected behaviour."
            )

        if self.dependencies["glib"].options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Linking shared glib with the MSVC static runtime is not supported")

    def build_requirements(self):
        self.tool_requires("meson/1.1.0")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

        tc = MesonToolchain(self)
        tc.project_options.update({
            "build-examples": "false",
            "build-documentation": "false",
            "msvc14x-parallel-installable": "false"
        })
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        meson_build = os.path.join(self.source_folder, "meson.build")
        replace_in_file(self, meson_build, "subdir('tests')", "")
        if is_msvc(self):
            # GLiBMM_GEN_EXTRA_DEFS_STATIC is not defined anywhere and is not
            # used anywhere except here
            # when building a static build !defined(GLiBMM_GEN_EXTRA_DEFS_STATIC)
            # evaluates to 0
            if not self.options.shared:
                replace_in_file(self,
                                      os.path.join(self.source_folder, "tools",
                                                   "extra_defs_gen", "generate_extra_defs.h"),
                                      "#if defined (_MSC_VER) && !defined (GLIBMM_GEN_EXTRA_DEFS_STATIC)",
                                      "#if 0",
                                      )

            # when using cpp_std=c++NM the /permissive- flag is added which
            # attempts enforcing standard conformant c++ code
            # the problem is that older versions of Windows SDK is not standard
            # conformant! see:
            # https://developercommunity.visualstudio.com/t/error-c2760-in-combaseapih-with-windows-sdk-81-and/185399
            replace_in_file(self, meson_build, "cpp_std=c++", "cpp_std=vc++")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        def rename_msvc_static_libs():
            lib_folder = os.path.join(self.package_folder, "lib")
            rename(self, os.path.join(lib_folder, f"libglibmm-{self._abi_version}.a"),
                   os.path.join(lib_folder, f"{self._glibmm_lib}.lib"))
            rename(self, os.path.join(lib_folder, f"libgiomm-{self._abi_version}.a"),
                   os.path.join(lib_folder, f"{self._giomm_lib}.lib"))
            rename(self, os.path.join(lib_folder, f"libglibmm_generate_extra_defs-{self._abi_version}.a"),
                   os.path.join(lib_folder, f"glibmm_generate_extra_defs-{self._abi_version}.lib"))

        meson = Meson(self)
        meson.install()

        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))

        if is_msvc(self):
            rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
            if not self.options.shared:
                rename_msvc_static_libs()

        for directory in [self._glibmm_lib, self._giomm_lib]:
            directory_path = os.path.join(self.package_folder, "lib", directory, "include", "*.h")
            for header_file in glob.glob(directory_path):
                shutil.move(
                    header_file,
                    os.path.join(self.package_folder, "include", directory, os.path.basename(header_file)),
                )

        for dir_to_remove in ["pkgconfig", self._glibmm_lib, self._giomm_lib]:
            rmdir(self, os.path.join(self.package_folder, "lib", dir_to_remove))
        fix_apple_shared_install_name(self)

    def package_info(self):
        glibmm_component = f"glibmm-{self._abi_version}"
        self.cpp_info.components[glibmm_component].set_property("pkg_config_name", glibmm_component)
        self.cpp_info.components[glibmm_component].libs = [glibmm_component]
        self.cpp_info.components[glibmm_component].includedirs = [os.path.join("include", glibmm_component)]
        self.cpp_info.components[glibmm_component].requires = ["glib::gobject-2.0", "libsigcpp::libsigcpp"]

        giomm_component = f"giomm-{self._abi_version}"
        self.cpp_info.components[giomm_component].set_property("pkg_config_name", giomm_component)
        self.cpp_info.components[giomm_component].libs = [giomm_component]
        self.cpp_info.components[giomm_component].includedirs = [os.path.join("include", giomm_component)]
        self.cpp_info.components[giomm_component].requires = [glibmm_component, "glib::gio-2.0"]
