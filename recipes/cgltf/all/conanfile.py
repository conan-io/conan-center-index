import os

from conans import ConanFile, tools

class CgltfConan(ConanFile):
    name = "cgltf"
    description = "Single-file glTF 2.0 loader and writer written in C99."
    license = "MIT"
    topics = ("conan", "cgltf", "gltf", "header-only")
    homepage = "https://github.com/jkuhlmann/cgltf"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        for header_file in ["cgltf.h", "cgltf_write.h"]:
            self.copy(header_file, dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
