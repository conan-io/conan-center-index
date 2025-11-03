from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, collect_libs
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0"


class ImathConan(ConanFile):
    name = "imath"
    description = (
        "Imath is a C++ and python library of 2D and 3D vector, matrix, and "
        "math operations for computer graphics."
    )
    license = "BSD-3-Clause"
    topics = ("computer-graphics", "matrix", "openexr", "3d-vector")
    homepage = "https://github.com/AcademySoftwareFoundation/Imath"
    url = "https://github.com/conan-io/conan-center-index"

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

    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_TESTING"] = False
        if is_msvc(self) and self.settings.compiler.get_safe("cppstd"):
            # when msvc is working with a C++ standard level higher
            # than the default, we need the __cplusplus macro to be correct
            tc.variables["CMAKE_CXX_FLAGS"] = "/Zc:__cplusplus"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Imath")
        self.cpp_info.set_property("cmake_target_name", "Imath::Imath")
        self.cpp_info.set_property("pkg_config_name", "Imath")

        # Imath::ImathConfig - header only library
        imath_config = self.cpp_info.components["imath_config"]
        imath_config.set_property("cmake_target_name", "Imath::ImathConfig")
        imath_config.includedirs.append(os.path.join("include", "Imath"))

        # Imath::Imath - linkable library
        imath_lib = self.cpp_info.components["imath_lib"]
        imath_lib.set_property("cmake_target_name", "Imath::Imath")
        imath_lib.set_property("pkg_config_name", "Imath")
        imath_lib.libs = collect_libs(self)
        imath_lib.requires = ["imath_config"]
        if self.settings.os == "Windows" and self.options.shared:
            imath_lib.defines.append("IMATH_DLL")
