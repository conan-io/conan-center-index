from conan import ConanFile
from conan.errors import ConanException
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class ZopfliConan(ConanFile):
    name = "zopfli"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/zopfli/"
    description = (
        "Zopfli Compression Algorithm is a compression library programmed in C "
        "to perform very good, but slow, deflate or zlib compression."
    )
    topics = ("compression", "deflate", "gzip", "zlib")
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
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ZOPFLI_BUILD_INSTALL"] = True
        tc.variables["CMAKE_MACOSX_BUNDLE"] = False
        # Generate a relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        if Version(self.version) > "1.0.3": # pylint: disable=conan-unreachable-upper-version
            raise ConanException("CMAKE_POLICY_VERSION_MINIMUM hardcoded to 3.5, check if new version supports CMake 4")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Zopfli")

        self.cpp_info.components["libzopfli"].set_property("cmake_target_name", "Zopfli::libzopfli")
        self.cpp_info.components["libzopfli"].libs = ["zopfli"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libzopfli"].system_libs = ["m"]

        self.cpp_info.components["libzopflipng"].set_property("cmake_target_name", "Zopfli::libzopflipng")
        self.cpp_info.components["libzopflipng"].libs = ["zopflipng"]
        self.cpp_info.components["libzopflipng"].requires = ["libzopfli"]
