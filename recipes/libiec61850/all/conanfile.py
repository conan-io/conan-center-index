import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rm, rmdir

required_conan_version = ">=2.1"

class Libiec61850Conan(ConanFile):
    name = "libiec61850"
    description = "An open-source library for the IEC 61850 protocols."
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libiec61850.com/libiec61850"
    topics = ("iec61850", "mms", "goose", "sampled values")

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

    languages = ["C"]
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["WITH_MBEDTLS"] = False
        tc.cache_variables["FIND_PACKAGE_DISABLE_Doxygen"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        if self.settings.os == "Windows":
            target = "iec61850-shared" if self.options.get_safe("shared") else "iec61850"
            cmake.build(target=target)
        else:
            cmake.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        if self.settings.os == "Windows":
            cmake.install(component="Development")  # Install header files
            # Copy files manually no avoid messing with cmake install different targets mixing shared/static
            copy(self, "*.lib", self.build_folder, os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dll", self.build_folder, os.path.join(self.package_folder, "bin"), keep_path=False)
        else:
            cmake.install()

    def package_info(self):
        hal_lib =  "hal-shared" if self.options.get_safe("shared") else "hal"
        self.cpp_info.components["libiec61850"].libs = ["iec61850", hal_lib]
        self.cpp_info.components["libiec61850"].set_property("pkg_config_name", "iec61850")
        if self.settings.os in ["Linux"]:
            self.cpp_info.components["libiec61850"].system_libs.append("pthread")
            self.cpp_info.components["libiec61850"].system_libs.append("rt")
