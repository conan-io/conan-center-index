from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class ChunkIOConan(ConanFile):
    name = "chunkio"
    description = "Simple library to manage chunks of data in memory and file system"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/edsiper/chunkio"
    topics = ("chunk", "io", "memory", "file")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_filesystem": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_filesystem": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

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
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["CIO_LIB_STATIC"] = not self.options.shared
        tc.variables["CIO_LIB_SHARED"] = self.options.shared
        tc.variables["CIO_BACKEND_FILESYSTEM"] = self.options.with_filesystem
        # Relocatable shared libs on macOS
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["chunkio-shared"] if self.options.shared else ["chunkio-static", "cio-crc32"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("shlwapi")
