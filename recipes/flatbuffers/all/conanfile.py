import glob
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

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FLATBUFFERS_BUILD_TESTS"] = False
        self._cmake.definitions["FLATBUFFERS_BUILD_SHAREDLIB"] = self.options.shared
        self._cmake.definitions["FLATBUFFERS_BUILD_FLATLIB"] = not self.options.shared
        self._cmake.definitions["FLATBUFFERS_BUILD_FLATC"] = False
        self._cmake.definitions["FLATBUFFERS_BUILD_FLATHASH"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

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
                tools.mkdir(os.path.join(self.package_folder, "bin"))
                for dll_path in glob.glob(os.path.join(self.package_folder, "lib", "*.dll")):
                    shutil.move(dll_path, os.path.join(self.package_folder, "bin", os.path.basename(dll_path)))

    def package_info(self):
        if not self.options.header_only:
            self.cpp_info.libs = tools.collect_libs(self)
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.append("m")
