from conans import ConanFile, CMake, tools
import os
import shutil


class OpenexrConan(ConanFile):
    name = "openexr"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/openexr/openexr"
    topics = ("conan")
    license = "BSD-3"
    description = "OpenEXR is a high dynamic-range (HDR) image file format for use in computer imaging applications"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, 'fPIC': True}
    generators = "cmake"

    exports_sources = ["CMakeLists.txt"]

    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "openexr-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def requirements(self):
        self.requires.add("zlib/1.2.11")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ZLIB_LIBRARY"] = self.deps_cpp_info["zlib"].libs[0]
        cmake.definitions["ZLIB_INCLUDE_DIR"] = self.deps_cpp_info["zlib"].include_paths[0]
        cmake.definitions["BUILD_TESTING"] = "OFF"
        cmake.definitions["OPENEXR_VIEWERS_ENABLE"] = "OFF"
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = CMake(self)
        cmake = self._configure_cmake()
        cmake.install()

    def package(self):
        cmake = CMake(self)
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
