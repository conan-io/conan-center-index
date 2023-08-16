from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=1.53.0"


class BacnetStackConan(ConanFile):
    name = "bacnet-stack"
    license = "GPL-2.0-or-later"
    homepage = "https://github.com/bacnet-stack/bacnet-stack/"
    url = "https://github.com/conan-io/conan-center-index"
    description = """
        BACnet Protocol Stack library provides a BACnet application layer,
        network layer and media access (MAC) layer communications services."""
    topics = ("bacnet")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True
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
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BACNET_STACK_BUILD_APPS"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="gpl-2.txt", dst=os.path.join(self.package_folder, "licenses"), src=os.path.join(self.source_folder, "license"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "bacnet-stack", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["bacnet-stack"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
        if not self.options.shared:
            self.cpp_info.defines = ["BACNET_STACK_STATIC_DEFINE"]
        self.cpp_info.set_property("cmake_file_name", "bacnet-stack")
        self.cpp_info.set_property("cmake_target_name", "bacnet-stack::bacnet-stack")
