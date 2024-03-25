from conan import ConanFile
from conan.tools.files import copy, get, collect_libs, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.gnu import PkgConfigDeps
from conan.tools.meson import Meson, MesonToolchain
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
import os

required_conan_version = ">=1.53"

class LibvaConan(ConanFile):
    name = "libva"
    description = "Libva is an implementation for VA-API (Video Acceleration API)"
    topics = ("libva")
    license = "MIT"
    homepage = "https://github.com/intel/libva"
    url = "https://gitlab.com/missionrobotics/conan-packages/mr-conan-index"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disable_drm": [True, False],
        "with_x11": [True, False],
        "with_glx": [True, False],
        "with_wayland": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disable_drm": False,
        "with_x11": True,
        "with_glx": False,
        "with_wayland": False,
    }

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.build_requires("meson/1.3.1")
        self.build_requires("pkgconf/2.1.0")

    def requirements(self):
        if not self.options.disable_drm:
            self.requires( "libdrm/2.4.119" )
        if self.options.with_x11:
            self.requires("xorg/system")
        if self.options.with_glx:
            raise ConanInvalidConfiguration("GL not yet supported")
        if self.options.with_wayland:
            raise ConanInvalidConfiguration("Wayland not yet supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

        tc = MesonToolchain(self)
        tc.project_options.update({
            "disable_drm": "true" if self.options.disable_drm else "false",
            "with_x11": "yes" if self.options.with_x11 else "no",
            "with_glx": "yes" if self.options.with_glx else "no",
            "with_wayland": "yes" if self.options.with_wayland else "no"
        })
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "libva")
        self.cpp_info.set_property("cmake_target_name", "libva::libva")
        self.cpp_info.set_property("pkg_config_name", "libva")

        self.cpp_info.components["va"].set_property("cmake_target_name", "libva::va")
        self.cpp_info.components["va"].set_property("pkg_config_name", "libva")
        self.cpp_info.components["va"].names["pkg_config"] = "libva"
        self.cpp_info.components["va"].libs = ["va"]

        if not self.options.disable_drm:
            self.cpp_info.components["va-drm"].set_property("cmake_target_name", "libva::va-drm")
            self.cpp_info.components["va-drm"].set_property("pkg_config_name", "libva-drm")
            self.cpp_info.components["va-drm"].names["pkg_config"] = "libva-drm"
            self.cpp_info.components["va-drm"].libs = ["va-drm"]
            self.cpp_info.components["va-drm"].requires.append( "libdrm::libdrm" )

        if self.options.with_x11:
            self.cpp_info.components["va-x11"].set_property("cmake_target_name", "libva::va-x11")
            self.cpp_info.components["va-x11"].set_property("pkg_config_name", "libva-x11")
            self.cpp_info.components["va-x11"].names["pkg_config"] = "libva-x11"
            self.cpp_info.components["va-x11"].libs = ["va-x11"]
            self.cpp_info.components["va-x11"].requires.append( "xorg::xorg" )

        self.cpp_info.names["cmake_find_package"] = "libva"
        self.cpp_info.names["cmake_find_package_multi"] = "libva"
        self.cpp_info.components["va"].names["cmake_find_package"] = "va"
        self.cpp_info.components["va"].names["cmake_find_package_multi"] = "va"