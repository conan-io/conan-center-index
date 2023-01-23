from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os

class NanoPbConan(ConanFile):
    name = "nanopb"
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Protocol Buffers with small code size"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("protobuf/3.21.9")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        if is_msvc(self):
            tc.variables["nanopb_MSVC_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package_info(self):
        self.cpp_info.libs = ["protobuf-nanopb"]
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(os.path.join("extra"))

    def package(self):
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "local"))

        copy(self, "*", 
             os.path.join(self.source_folder, "generator"),
             os.path.join(self.package_folder, "generator"))

        copy(self, "pb_decode.c", self.source_folder, self.package_folder)
        copy(self, "pb_encode.c", self.source_folder, self.package_folder)
        copy(self, "pb_common.c", self.source_folder, self.package_folder)

        copy(self, "FindNanopb.cmake", 
             os.path.join(self.source_folder, "extra"),
             os.path.join(self.package_folder, "extra"))

