import os
from conans import CMake, ConanFile, tools

class EasyExifConan(ConanFile):
    name = "easyexif"
    description = "Tiny ISO-compliant C++ EXIF parsing library, third-party dependency free."
    topics = ("conan", "exif", "image", "multimedia", "format", "graphics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mayanklahiri/easyexif"
    license = "https://github.com/mayanklahiri/easyexif/blob/master/LICENSE"
    exports_sources = "CMakeLists.txt"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = ["easyexif"]
