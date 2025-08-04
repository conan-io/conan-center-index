from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.1"


class LibvplConan(ConanFile):
    name = "libvpl"
    description = "Intel® Video Processing Library (Intel® VPL) provides a single video processing API for encode, decode, and video processing that works across a wide range of accelerators."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/intel/libvpl"
    topics = ("video", "processing", "intel", "encode", "decode")
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

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("libdrm/2.4.124")
            self.requires("libva/2.21.0")
            self.requires("xorg/system")
            self.requires("wayland/1.22.0")
            self.requires("wayland-protocols/1.45")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "vpl")
        self.cpp_info.set_property("cmake_target_name", "VPL::VPL")
        self.cpp_info.set_property("cmake_target_aliases", ["VPL::dispatcher"])
        self.cpp_info.set_property("pkg_config_name", "vpl")
        self.cpp_info.libs = ["vpl"]

        # Add system libraries if needed
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["advapi32"]

