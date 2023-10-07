from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class IowowConan(ConanFile):
    name = "iowow"
    description = "The skiplist based persistent key/value storage engine"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Softmotions/iowow"
    topics = ("database", "nosql", "key-value", "kvstore", "skiplist", "ejdb")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["PACKAGE_ZIP"] = False
        tc.variables["PACKAGE_TGZ"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))


    def package_info(self):
        self.cpp_info.libs = ["iowow-1"]
        self.cpp_info.set_property("pkg_config_name", "package")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("m")
