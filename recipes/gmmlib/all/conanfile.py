from conan import ConanFile
from conan.tools.files import copy, get, collect_libs, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53"

class GmmlibConan(ConanFile):
    name = "gmmlib"
    description = "Provides device specific and buffer management for the Intel Media Driver for VAAPI"
    topics = ("gmmlib", "vaapi")
    homepage = "https://github.com/intel/gmmlib"
    url = "https://gitlab.com/missionrobotics/conan-packages/mr-conan-index"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
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

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["igdgmm"].set_property("pkg_config_name", "igdgmm")
        self.cpp_info.components["igdgmm"].names["pkg_config"] = "igdgmm"
        self.cpp_info.components["igdgmm"].libs = collect_libs(self)
        self.cpp_info.components["igdgmm"].system_libs = ["pthread"]   

        self.cpp_info.components["igdgmm"].defines = ["GMM_LIB_DLL"]

        self.cpp_info.components["igdgmm"].includedirs.append( os.path.join("include", "igdgmm/GmmLib/inc ") )
        self.cpp_info.components["igdgmm"].includedirs.append( os.path.join("include", "igdgmm/inc") )
        self.cpp_info.components["igdgmm"].includedirs.append( os.path.join("include", "igdgmm/inc/common") )
        self.cpp_info.components["igdgmm"].includedirs.append( os.path.join("include", "igdgmm/util") )





