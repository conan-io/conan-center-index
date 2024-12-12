from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rm, rmdir
from os.path import join

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
        tc.cache_variables["FIND_PACKAGE_DISABLE_Doxygen"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        target = "iec61850-shared" if self.options.get_safe("shared") else "iec61850"
        cmake.build(target=target)

    def package(self):
        copy(self, "COPYING", self.source_folder, join(self.package_folder, "licenses"))
        rm(self, "*.la", join(self.package_folder, "lib"))
        rmdir(self, join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, join(self.package_folder, "share"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["libiec61850"].libs = ["iec61850"]
        self.cpp_info.components["libiec61850"].set_property("pkg_config_name", "iec61850")
        if self.settings.os in ["Linux"]:
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("rt")
