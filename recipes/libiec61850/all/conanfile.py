import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy

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
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.cache_variables["FIND_PACKAGE_DISABLE_Doxygen"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        target = "iec61850-shared" if self.options.get_safe("shared") else "iec61850"
        cmake.build(target=target)

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install(component="Development")  # Install header files
        # Copy files manually because upstream CMakeLists tries to install both shared and static at once
        copy(self, "*.so*", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*hal.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*iec61850.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.components["libiec61850"].libs = ["iec61850"]
        if self.options.get_safe("shared") == False:
            self.cpp_info.components["libiec61850"].libs.append("hal")
        self.cpp_info.components["libiec61850"].set_property("pkg_config_name", "iec61850")
        if self.settings.os in ["Linux"]:
            self.cpp_info.components["libiec61850"].system_libs.append("pthread")
            self.cpp_info.components["libiec61850"].system_libs.append("rt")
