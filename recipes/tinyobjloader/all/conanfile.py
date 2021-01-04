import os
from conans import ConanFile, CMake, tools


class TinyObjLoaderConan(ConanFile):
    name = "tinyobjloader"
    description = "Tiny but powerful single file wavefront obj loader"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, "fPIC": True}
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/syoyo/tinyobjloader"
    topics = ("conan", "tinyobjloader", "wavefront", "geometry")
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + '-' + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        if self.settings.os == "Windows" and self.options.shared:
            cmake.definitions["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        cmake.definitions["TINYOBJLOADER_COMPILATION_SHARED"] = self.options.shared
        cmake.definitions["CMAKE_INSTALL_DOCDIR"] = "licenses"
        cmake.configure(build_dir=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "tinyobjloader"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
