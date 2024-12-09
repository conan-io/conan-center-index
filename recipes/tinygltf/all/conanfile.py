from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get, replace_in_file
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.51.1"


class TinygltfConan(ConanFile):
    name = "tinygltf"
    description = "Header only C++11 tiny glTF 2.0 library."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/syoyo/tinygltf"
    topics = ("gltf", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "draco": [True, False],
        "stb_image": [True, False],
        "stb_image_write": [True, False],
    }
    default_options = {
        "draco": False,
        "stb_image": True,
        "stb_image_write": True,
    }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        self.requires("nlohmann_json/3.11.3")
        if self.options.draco:
            self.requires("draco/1.5.6")
        if self.options.stb_image or self.options.stb_image_write:
            self.requires("stb/cci.20230920")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        replace_in_file(self, os.path.join(self.source_folder, "tiny_gltf.h"),
                              "#include \"json.hpp\"",
                              "#include <nlohmann/json.hpp>")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "tiny_gltf.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TinyGLTF")
        self.cpp_info.set_property("cmake_target_name", "TinyGLTF::TinyGLTF")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.options.draco:
            self.cpp_info.defines.append("TINYGLTF_ENABLE_DRACO")
        if not self.options.stb_image:
            self.cpp_info.defines.append("TINYGLTF_NO_STB_IMAGE")
        if not self.options.stb_image_write:
            self.cpp_info.defines.append("TINYGLTF_NO_STB_IMAGE_WRITE")

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "TinyGLTF"
        self.cpp_info.names["cmake_find_package_multi"] = "TinyGLTF"
