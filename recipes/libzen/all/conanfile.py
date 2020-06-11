import os
from conans import ConanFile, CMake, tools


class LibzenConan(ConanFile):
    name = "libzen"
    license = "ZLIB"
    homepage = "https://github.com/MediaArea/ZenLib"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Small C++ derivate classes to have an easier life"
    topics = ("conan", "libzen", "c++", "helper", "util")
    settings = "os",  "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_unicode": [True, False],
        "enable_large_files": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_unicode": True,
        "enable_large_files": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ZenLib", self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_UNICODE"] = self.options.enable_unicode
        self._cmake.definitions["LARGE_FILES"] = self.options.enable_large_files
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("License.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        suffix = ""
        if self.settings.build_type == "Debug":
            if self.settings.os == "Windows":
                suffix = "d"
            elif tools.is_apple_os(self.settings.os):
                suffix = "_debug"
        self.cpp_info.libs = ["zen{}".format(suffix)]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m", "pthread"])
        if self.options.enable_unicode:
            self.cpp_info.defines.append("UNICODE")
        self.cpp_info.names["cmake_find_package"] = "ZenLib"
        self.cpp_info.names["cmake_find_package_multi"] = "ZenLib"
