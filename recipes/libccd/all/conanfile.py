import os

from conans import ConanFile, CMake, tools

class LibccdConan(ConanFile):
    name = "libccd"
    description = "Library for collision detection between two convex shapes."
    license = "BSD-3-Clause"
    topics = ("conan", "libccd", "collision", "3d")
    homepage = "https://github.com/danfis/libccd"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_double_precision": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_double_precision": False
    }

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
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "${CMAKE_BINARY_DIR}", "${CMAKE_CURRENT_BINARY_DIR}")
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_DOCUMENTATION"] = False
        self._cmake.definitions["ENABLE_DOUBLE_PRECISION"] = self.options.enable_double_precision
        self._cmake.definitions["CCD_HIDE_ALL_SYMBOLS"] = not self.options.shared
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("BSD-LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "ccd"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "ccd"
        self.cpp_info.names["cmake_find_package_multi"] = "ccd"
        self.cpp_info.names["pkg_config"] = "ccd"
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append("CCD_STATIC_DEFINE")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
