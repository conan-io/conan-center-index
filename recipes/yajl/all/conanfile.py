from conan import ConanFile
from conan.tools.files import get, copy, rmdir, rename
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.apple import fix_apple_shared_install_name
import os

required_conan_version = ">=1.53.0"


class YAJLConan(ConanFile):
    name = "yajl"
    description = "A fast streaming JSON parsing library in C"
    license = "ISC"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lloyd/yajl"
    topics = ("json", "encoding", "decoding", "manipulation")
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
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))

        # We need to move the dll from lib to bin in order for it to be found later
        if self.settings.os == "Windows":
            rename(self, os.path.join(self.package_folder, "lib", "yajl.dll"), os.path.join(self.package_folder, "bin", "yajl.dll"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["yajl"]

        # https://github.com/lloyd/yajl/blob/5e3a7856e643b4d6410ddc3f84bc2f38174f2872/src/CMakeLists.txt#L64
        self.cpp_info.set_property("pkg_config_name", "yajl")

        if self.options.shared:
            self.cpp_info.libs = ["yajl"]
        else:
            self.cpp_info.libs = ["yajl_s"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "YAJL"
        self.cpp_info.filenames["cmake_find_package_multi"] = "yajl"
        self.cpp_info.names["cmake_find_package"] = "YAJL"
        self.cpp_info.names["cmake_find_package_multi"] = "yajl"
