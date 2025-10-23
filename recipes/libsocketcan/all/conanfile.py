import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, apply_conandata_patches

class LibSocketCANConan(ConanFile):
    name = "socketcan"
    license = "GNU Lesser General Public License v2.1"
    author = "linux-can"
    url = "https://github.com/linux-can/libsocketcan/"
    description = "This is libsocketcan, a userspace library to do some common tasks while dealing with the socketcan Framework."
    topics = ("socketcan", "can-bus", "can")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "*"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination="src")
        apply_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        cmake_toolchain = CMakeToolchain(self)
        cmake_toolchain.generate()

        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="*.h", src=os.path.join(self.source_folder, "src", "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, pattern="*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.so", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, pattern="*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["socketcan"]
