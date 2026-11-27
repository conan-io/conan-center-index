from conan import ConanFile
from conan.tools.build import check_min_cstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
import os

required_conan_version = ">=2.4"


class TinygltfConan(ConanFile):
    name = "tinygltf"
    description = "C11 glTF 2.0 loader and writer with arena based memory management."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/syoyo/tinygltf"
    topics = ("gltf", "3d", "graphics")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    languages = "C"
    implements = ["auto_shared_fpic"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def validate(self):
        if self.settings.get_safe("compiler.cstd"):
            check_min_cstd(self, 11)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TINYGLTF3_ENABLE_FS"] = True
        tc.variables["TINYGLTF3_BUILD_TESTS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TinyGLTF")
        self.cpp_info.set_property("cmake_target_name", "TinyGLTF::TinyGLTF")
        self.cpp_info.libs = ["tinygltf"]
