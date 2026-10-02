from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os

required_conan_version = ">=2.0"


class TinygltfConan(ConanFile):
    name = "tinygltf"
    description = "C11 glTF 2.0 loader and writer with arena based memory management."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/syoyo/tinygltf"
    topics = ("gltf", "3d", "graphics")
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

    exports_sources = "CMakeLists.txt"

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
        tc.variables["TINYGLTF_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["TINYGLTF_ENABLE_FS"] = self.options.with_filesystem
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TinyGLTF")
        self.cpp_info.set_property("cmake_target_name", "TinyGLTF::TinyGLTF")
        self.cpp_info.libs = ["tinygltf"]
