from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class LibnfsConan(ConanFile):
    name = "libnfs"
    description = "LIBNFS is a client library for accessing NFS shares over a network."
    topics = ("async", "nfsv4", "nfs")
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/sahlberg/libnfs"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_multithreading": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_multithreading": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "6.0.2":
            del self.options.with_multithreading

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        if Version(self.version) >= "6.0.2":
            self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_MULTITHREADING"] = self.options.get_safe("with_multithreading")
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENCE*.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libnfs")
        self.cpp_info.set_property("cmake_target_name", "libnfs::libnfs")
        self.cpp_info.set_property("pkg_config_name", "libnfs")
        if Version(self.version) >= "6.0.2" and self.settings.os == "Windows":
            self.cpp_info.libs = ["libnfs"]
        else:
            self.cpp_info.libs = ["nfs"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
