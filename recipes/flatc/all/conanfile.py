"""Conan recipe package for Google FlatBuffers - Flatc
"""
import os
from conan import ConanFile, tools
from conans import CMake


class FlatcConan(ConanFile):
    name = "flatc"
    deprecated = "flatbuffers"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://google.github.io/flatbuffers/"
    topics = ("conan", "flatbuffers", "serialization", "rpc", "json-parser", "installer")
    description = "Memory Efficient Serialization Library"
    settings = "os", "arch"
    exports_sources = ["CMakeLists.txt","patches/**"]
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.files.patch(self, **patch)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "flatbuffers-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["FLATBUFFERS_BUILD_TESTS"] = False
        cmake.definitions["FLATBUFFERS_BUILD_SHAREDLIB"] = False
        cmake.definitions["FLATBUFFERS_BUILD_FLATLIB"] = True
        cmake.definitions["FLATBUFFERS_BUILD_FLATC"] = True
        cmake.definitions["FLATBUFFERS_BUILD_FLATHASH"] = True
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        extension = ".exe" if self.settings.os == "Windows" else ""
        bin_dir = os.path.join(self._build_subfolder, "bin")
        self.copy(pattern="flatc" + extension, dst="bin", src=bin_dir)
        self.copy(pattern="flathash" + extension, dst="bin", src=bin_dir)
        self.copy(pattern="BuildFlatBuffers.cmake", dst="bin/cmake", src=os.path.join(self._source_subfolder,"CMake"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.PATH.append(bin_path)
        self.cpp_info.builddirs.append("bin/cmake")
        self.cpp_info.build_modules.append("bin/cmake/BuildFlatBuffers.cmake")
