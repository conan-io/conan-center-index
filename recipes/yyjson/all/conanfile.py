from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class YyjsonConan(ConanFile):
    name = "yyjson"
    description = "A high performance JSON library written in ANSI C."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ibireme/yyjson"
    topics = ("json", "serialization", "deserialization")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_utf8_validation": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_utf8_validation": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "0.8.0":
            del self.options.with_utf8_validation

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
        if Version(self.version) >= "0.8.0":
            tc.variables["YYJSON_DISABLE_UTF8_VALIDATION"] = not bool(self.options.with_utf8_validation)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "yyjson")
        self.cpp_info.set_property("cmake_target_name", "yyjson::yyjson")
        self.cpp_info.libs = ["yyjson"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("YYJSON_IMPORTS")

        if Version(self.version) >= "0.9.0":
            self.cpp_info.set_property("pkg_config_name", "yyjson")
