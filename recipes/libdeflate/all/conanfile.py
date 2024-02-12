from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, rmdir
import os

required_conan_version = ">=1.53.0"


class LibdeflateConan(ConanFile):
    name = "libdeflate"
    description = "Heavily optimized library for DEFLATE/zlib/gzip compression and decompression."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ebiggers/libdeflate"
    topics = ("compression", "decompression", "deflate", "zlib", "gzip")
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
        tc.variables["LIBDEFLATE_BUILD_STATIC_LIB"] = not self.options.shared
        tc.variables["LIBDEFLATE_BUILD_SHARED_LIB"] = self.options.shared
        tc.variables["LIBDEFLATE_BUILD_GZIP"] = False
        tc.variables["LIBDEFLATE_BUILD_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libdeflate")
        target_suffix = "_shared" if self.options.shared else "_static"
        self.cpp_info.set_property("cmake_target_name", f"libdeflate::libdeflate{target_suffix}")
        self.cpp_info.set_property("cmake_target_aliases", ["libdeflate::libdeflate"]) # not official, avoid to break users
        self.cpp_info.set_property("pkg_config_name", "libdeflate")
        # TODO: back to global scope in conan v2
        self.cpp_info.components["_libdeflate"].libs = collect_libs(self)
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["_libdeflate"].defines.append("LIBDEFLATE_DLL")

        # TODO: to remove in conan v2
        self.cpp_info.components["_libdeflate"].names["cmake_find_package"] = f"libdeflate{target_suffix}"
        self.cpp_info.components["_libdeflate"].names["cmake_find_package_multi"] = f"libdeflate{target_suffix}"
        self.cpp_info.components["_libdeflate"].set_property("cmake_target_name", f"libdeflate::libdeflate{target_suffix}")
        self.cpp_info.components["_libdeflate"].set_property("pkg_config_name", "libdeflate")
