from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.0.0"


class Blake3Conan(ConanFile):
    name = "blake3"
    description = "BLAKE3 is a cryptographic hash function that is much faster than MD5, SHA-1, SHA-2, SHA-3, and BLAKE2."
    license = "CC0-1.0 OR Apache-2.0 OR Apache-2.0 WITH LLVM-exception"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/BLAKE3-team/BLAKE3"
    topics = ("blake3", "hash", "crypto", "cryptography")
    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tbb": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tbb": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_tbb:
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_tbb:
            self.requires("onetbb/[>=2021.12.0 <2024.0.0]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BLAKE3_USE_TBB"] = self.options.with_tbb
        tc.cache_variables["BLAKE3_FETCH_TBB"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "c"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE_A2", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE_A2LLVM", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE_CC0", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self,os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self,os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "blake3")
        self.cpp_info.set_property("cmake_target_name", "BLAKE3::blake3")
        self.cpp_info.set_property("pkg_config_name", "libblake3")
        self.cpp_info.libs = ["blake3"]
        if self.options.with_tbb:
            self.cpp_info.requires = ["onetbb::libtbb"]
            self.cpp_info.defines.append("BLAKE3_USE_TBB")
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("BLAKE3_DLL")
