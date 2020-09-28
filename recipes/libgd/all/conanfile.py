import glob
import os
from conans import ConanFile, tools, CMake


class LibgdConan(ConanFile):
    name = "libgd"
    license = "BSD-like"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("GD is an open source code library for the dynamic "
                   "creation of images by programmers.")
    topics = ("images", "graphics")
    settings = "os", "compiler", "build_type", "arch"
    homepage = "https://libgd.github.io"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"
    requires = "zlib/1.2.11"
    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _patch(self):
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(cmakelists, "${CMAKE_SOURCE_DIR}", "${CMAKE_CURRENT_SOURCE_DIR}")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("libgd-*")[0], self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions['BUILD_STATIC_LIBS'] = not self.options.shared
        zlib_info = self.deps_cpp_info["zlib"]
        self._cmake.definitions["ZLIB_LIBRARY"] = zlib_info.libs[0]
        self._cmake.definitions["ZLIB_INCLUDE_DIR"] = zlib_info.include_paths[0]
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("COPYING", src=self._source_subfolder, dst="licenses",
                  ignore_case=True, keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, 'share'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.names["pkg_config"]= "gdlib"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == 'Windows' and not self.options.shared:
            self.cpp_info.defines.append('BGD_NONDLL')
            self.cpp_info.defines.append('BGDWIN32')
