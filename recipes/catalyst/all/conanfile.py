from conan import ConanFile
from conan.errors import ConanException
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, rmdir
import os

required_conan_version = ">=1.53.0"


class CatalystConan(ConanFile):
    name = "catalyst"
    package_type = "library"
    description = "Catalyst is an API specification developed for simulations (and other scientific data producers) to analyze and visualize data in situ."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.kitware.com/paraview/catalyst"
    topics = ("simulation", "visualization", "paraview", "in-situ", "in-transit")
    license = "BSD-3"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_mpi": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_mpi": False,
    }

    def build_requirements(self):
        self.tool_requires("cmake/[>3.26]")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def validate(self):
        # OpenMPI is not yet conan 2.0 compatible, so raise an exception in case its used
        if self.options.use_mpi:
            raise ConanException("MPI is not yet supported by the Catalyst recipe")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CATALYST_BUILD_REPLAY"] = False
        tc.variables["CATALYST_BUILD_TESTING"] = False
        tc.variables["CATALYST_BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["CATALYST_USE_MPI"] = False
        tc.variables["CATALYST_BUILD_TOOLS"] = False
        
        # Catalyst adds by default catalyst_${VERSION} as suffix for static libs. Remove that
        if not self.options.get_safe("shared"):
            tc.variables["CATALYST_CUSTOM_LIBRARY_SUFFIX"] = ""

        tc.generate()

        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "License.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "catalyst", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "catalyst")
        self.cpp_info.set_property("cmake_target_name", "catalyst::catalyst")
        self.cpp_info.set_property("pkg_config_name", "catalyst")


        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("dl")

        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            self.cpp_info.libs = [f"catalystd"]
        else:
            self.cpp_info.libs = ["catalyst"]


        # Includes are installed under catalyst-2.0, but official documentation says we should use -I<install_dir>/include/catalyst-2.0
        self.cpp_info.includedirs = ["include/catalyst-2.0"]

        self.cpp_info.names["cmake_find_package"] = "catalyst"
        self.cpp_info.names["cmake_find_package_multi"] = "catalyst"
