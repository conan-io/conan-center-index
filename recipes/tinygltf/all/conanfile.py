import os

from conans import ConanFile, tools

class TinygltfConan(ConanFile):
    name = "tinygltf"
    description = "Header only C++11 tiny glTF 2.0 library."
    license = "MIT"
    topics = ("conan", "tinygltf", "gltf")
    homepage = "https://github.com/syoyo/tinygltf"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "compiler"
    no_copy_source = True
    options = {
        "draco": [True, False],
        "stb_image": [True, False],
        "stb_image_write": [True, False],
    }
    default_options = {
        "draco": False,
        "stb_image": True,
        "stb_image_write": True
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, 11)

    def requirements(self):
        self.requires("nlohmann_json/3.9.1")
        if self.options.draco:
            self.requires("draco/1.3.6")
        if self.options.stb_image or self.options.stb_image_write:
            self.requires("stb/20200203")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "tiny_gltf.h"),
                              "#include \"json.hpp\"",
                              "#include <nlohmann/json.hpp>")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("tiny_gltf.h", dst="include", src=os.path.join(self.source_folder, self._source_subfolder))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "TinyGLTF"
        self.cpp_info.names["cmake_find_package_multi"] = "TinyGLTF"
        if self.options.draco:
            self.cpp_info.defines.append("TINYGLTF_ENABLE_DRACO")
        if not self.options.stb_image:
            self.cpp_info.defines.append("TINYGLTF_NO_STB_IMAGE")
        if not self.options.stb_image_write:
            self.cpp_info.defines.append("TINYGLTF_NO_STB_IMAGE_WRITE")
