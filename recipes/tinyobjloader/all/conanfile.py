import os
from conans import ConanFile, CMake, tools


class TinyObjLoaderConan(ConanFile):
    name = "tinyobjloader"
    description = "Tiny but powerful single file wavefront obj loader"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/syoyo/tinyobjloader"
    topics = ("conan", "tinyobjloader", "wavefront", "geometry")

    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "double": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "double": False,
    }

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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["TINYOBJLOADER_USE_DOUBLE"] = self.options.double
        self._cmake.definitions["TINYOBJLOADER_BUILD_TEST_LOADER"] = False
        self._cmake.definitions["TINYOBJLOADER_COMPILATION_SHARED"] = self.options.shared
        self._cmake.definitions["TINYOBJLOADER_BUILD_OBJ_STICHER"] = False
        self._cmake.definitions["CMAKE_INSTALL_DOCDIR"] = "licenses"
        self._cmake.configure(build_dir=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "tinyobjloader"))

    def package_info(self):
        suffix = "_double" if self.options.double else ""
        self.cpp_info.libs = ["tinyobjloader" + suffix]
        if self.options.double:
            self.cpp_info.defines.append("TINYOBJLOADER_USE_DOUBLE")
