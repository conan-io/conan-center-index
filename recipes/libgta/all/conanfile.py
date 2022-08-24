import os

from conans import ConanFile, CMake, tools

class LibgtaConan(ConanFile):
    name = "libgta"
    description = "Library that reads and writes GTA (Generic Tagged Arrays) files."
    license = "LGPL-2.1-or-later"
    topics = ("conan", "libgta", "gta")
    homepage = "https://marlam.de/gta"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "${CMAKE_SOURCE_DIR}", "${CMAKE_CURRENT_SOURCE_DIR}")
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["GTA_BUILD_STATIC_LIB"] = not self.options.shared
        self._cmake.definitions["GTA_BUILD_SHARED_LIB"] = self.options.shared
        self._cmake.definitions["GTA_BUILD_DOCUMENTATION"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "GTA"
        self.cpp_info.names["cmake_find_package_multi"] = "GTA"
        self.cpp_info.names["pkg_config"] = "gta"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.compiler == "Visual Studio" and not self.options.shared:
            self.cpp_info.defines.append("GTA_STATIC")
