from conan import ConanFile
from conan.tools.build import stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import msvc_runtime_flag
import os

required_conan_version = ">=1.54.0"


class IphreeqcConan(ConanFile):
    name = "iphreeqc"
    description = (
        "Library implementing the geochemical model PHREEQC. It is capable of "
        "simulating a wide range of equilibrium reactions between water and "
        "minerals, ion exchangers, surface complexes, solid solutions, and gases."
    )
    license = "FSFUL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.usgs.gov/software/phreeqc-version-3"
    topics = ("geochemistry", "modeling")
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
    def _is_cl_like(self):
        return self.settings.compiler.get_safe("runtime") is not None

    @property
    def _is_cl_like_static_runtime(self):
        return self._is_cl_like and "MT" in msvc_runtime_flag(self)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.20 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self._is_cl_like:
            tc.variables["IPHREEQC_STATIC_RUNTIME"] = self._is_cl_like_static_runtime
        tc.variables["IPHREEQC_ENABLE_MODULE"] = False
        tc.variables["IPHREEQC_FORTRAN_TESTING"] = False
        tc.variables["BUILD_CLR_LIBS"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "INSTALL", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "src"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "IPhreeqc")
        self.cpp_info.set_property("cmake_target_name", "IPhreeqc::IPhreeqc")
        postfix = ""
        if self.settings.build_type == "Debug":
            postfix += "d"
        elif self.settings.build_type == "MinSizeRel":
            postfix += "msr"
        elif self.settings.build_type == "RelWithDebInfo":
            postfix += "rwd"
        self.cpp_info.libs = [f"IPhreeqc{postfix}"]
        self.cpp_info.defines.append("IPHREEQC_NO_FORTRAN_MODULE")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
