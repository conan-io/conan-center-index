from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, rm, apply_conandata_patches, export_conandata_patches
import os


required_conan_version = ">=2.1"


class HsmcppConan(ConanFile):
    name = "hsmcpp"
    package_type = "static-library"
    description = "C++ based Hierarchical / Finite State Machine library oriented for embedded and RTOS systems"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/igor-krechetov/hsmcpp"
    topics = ("fsm", "hsm", "state-machine", "hierarchical", "embedded", "scxml")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["HSMBUILD_TARGET"] = "library"
        tc.cache_variables["HSMBUILD_PLATFORM"] = "windows" if self.settings.os == "Windows" else "posix"
        tc.cache_variables["HSMBUILD_TESTS"] = False
        tc.cache_variables["HSMBUILD_EXAMPLES"] = False
        tc.cache_variables["HSMBUILD_DEBUGGING"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*", os.path.join(self.package_folder, "lib", "cmake", "hsmcpp"), excludes="scxml2gen*")

    def package_info(self):
        # INFO: generateHsm() CMake macro
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake", "hsmcpp", "scxml2gen"))
        self.cpp_info.set_property("cmake_build_modules", [os.path.join("lib", "cmake", "hsmcpp", "scxml2gen", "CMakeLists.txt")])

        self.cpp_info.components["core"].libs = ["hsmcpp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["core"].system_libs.append("pthread")
        self.cpp_info.components["core"].defines = ["HSM_LOGGING_MODE_OFF", "HSM_ENABLE_SAFE_STRUCTURE"]

        self.cpp_info.components["std"].libs = ["hsmcpp_std"]
        self.cpp_info.components["std"].requires = ["core"]
