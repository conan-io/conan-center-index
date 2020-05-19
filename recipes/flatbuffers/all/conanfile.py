"""Conan recipe package for Google FlatBuffers
"""
import os
import shutil
from conans import ConanFile, CMake, tools


class FlatbuffersConan(ConanFile):
    name = "flatbuffers"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://google.github.io/flatbuffers"
    topics = ("conan", "flatbuffers", "serialization", "rpc", "json-parser")
    description = "Memory Efficient Serialization Library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "header_only": [True, False]}
    default_options = {"shared": False, "fPIC": True, "header_only": False}
    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["FLATBUFFERS_BUILD_TESTS"] = False
        cmake.definitions["FLATBUFFERS_BUILD_SHAREDLIB"] = self.options.shared
        cmake.definitions["FLATBUFFERS_BUILD_FLATLIB"] = not self.options.shared
        cmake.definitions["FLATBUFFERS_BUILD_FLATC"] = False
        cmake.definitions["FLATBUFFERS_BUILD_FLATHASH"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        if not self.options.header_only:
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        if self.options.header_only:
            header_dir = os.path.join(self._source_subfolder, "include", "flatbuffers")
            dst_dir = os.path.join("include", "flatbuffers")
            self.copy("*.h", dst=dst_dir, src=header_dir)
        else:
            cmake = self._configure_cmake()
            cmake.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
            if self.settings.os == "Windows" and self.options.shared:
                if self.settings.compiler == "Visual Studio":
                    tools.mkdir(os.path.join(self.package_folder, "bin"))
                    shutil.move(os.path.join(self.package_folder, "lib", "%s.dll" % self.name),
                                os.path.join(self.package_folder, "bin", "%s.dll" % self.name))
                elif self.settings.compiler == "gcc":
                    shutil.move(os.path.join(self.package_folder, "lib", "lib%s.dll" % self.name),
                                os.path.join(self.package_folder, "bin", "lib%s.dll" % self.name))

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()

    def package_info(self):
        if not self.options.header_only:
            self.cpp_info.libs = tools.collect_libs(self)
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.append("m")
