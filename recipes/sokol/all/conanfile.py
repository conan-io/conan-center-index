from conan import ConanFile, tools
import os
import glob


class SokolConan(ConanFile):
    name = "sokol"
    description = "Simple STB-style cross-platform libraries for C and C++, written in C."
    topics = ("sokol", "graphics", "3d")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/floooh/sokol"
    license = "Zlib"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()
