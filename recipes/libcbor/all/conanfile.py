from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=1.53.0"


class LibCborStackConan(ConanFile):
    name = "libcbor"
    license = "MIT"
    homepage = "https://github.com/PJK/libcbor"
    url = "https://github.com/conan-io/conan-center-index"
    description = "CBOR protocol implementation for C"
    topics = ("cbor", "serialization", "messaging")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "custom_alloc": [True, False],
        "pretty_printer": [True, False],
        "buffer_growth_factor": ["ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "custom_alloc": False,
        "pretty_printer": True,
        "buffer_growth_factor": 2,
    }

    def export_sources(self):
        export_conandata_patches(self)

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
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_EXAMPLES"] = False
        tc.variables["SANITIZE"] = False
        tc.variables["CBOR_CUSTOM_ALLOC"] = self.options.custom_alloc
        tc.variables["CBOR_PRETTY_PRINTER"] = self.options.pretty_printer
        tc.variables["CBOR_BUFFER_GROWTH"] = self.options.buffer_growth_factor
        # Relocatable shared libs on macOS
        tc.variables["CMAKE_MACOSX_RPATH"] = True
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libcbor")
        self.cpp_info.libs = ["cbor"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
