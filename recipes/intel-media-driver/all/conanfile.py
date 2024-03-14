from conan import ConanFile
from conan.tools.files import copy, get, collect_libs, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.gnu import PkgConfigDeps
from conan.errors import ConanInvalidConfiguration
import os
import textwrap
import shutil

required_conan_version = ">=1.53"


class IntelMediaDriverConan(ConanFile):
    name = "intel-media-driver"
    description = "VAAPI drivers for Intel graphics processors"
    topics = ("intel", "vaapi")
    homepage = "https://github.com/intel/media-driver"
    url = "https://gitlab.com/missionrobotics/conan-packages/mr-conan-index"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
    }

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows is not supported")
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
    
    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires( "libva/2.16.0" )
        self.requires( "gmmlib/22.3.3" )

    def build_requirements(self):
        self.tool_requires("pkgconf/1.9.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        pc = PkgConfigDeps(self)
        pc.generate()

        env = VirtualBuildEnv(self)
        env.generate()

        # Override Avahi's problematic check for the pkg-config executable.
        env = Environment()
        env.define("have_pkg_config", "yes")
        env.vars(self).save_script("conanbuild_pkg_config")

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "intel-media-driver")
        self.cpp_info.set_property("cmake_target_name", "intel-media-driver")
        self.cpp_info.set_property("pkg_config_name", "intel-media-driver")

        self.cpp_info.components["intel-media-driver"].libs = collect_libs(self)

        self.cpp_info.names["cmake_find_package"] = "intel-media-driver"
        self.cpp_info.names["cmake_find_package_multi"] = "intel-media-driver"
        self.cpp_info.names["pkg_config"] = "intel-media-driver"
