import os
from conan import ConanFile, tools
from conans import CMake


class LibconfigConan(ConanFile):
    name = "libconfig"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://hyperrealm.github.io/libconfig/"
    description = "C/C++ library for processing configuration files"
    topics = ("conan", "conf", "config", "cfg", "configuration")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake",
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        cmake = CMake(self)
        cmake.definitions['BUILD_EXAMPLES'] = False
        cmake.definitions['BUILD_TESTS'] = False
        cmake.configure(build_folder=self._build_subfolder)
        self._cmake = cmake
        return self._cmake

    def build(self):
        # https://github.com/hyperrealm/libconfig/issues/119
        tools.replace_in_file(os.path.join(self._source_subfolder, "lib", "CMakeLists.txt"), "_STDLIB_H", "")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["libconfig_"].names["cmake_find_package"] = "libconfig"
        self.cpp_info.components["libconfig_"].names["cmake_find_package_multi"] = "libconfig"
        self.cpp_info.components["libconfig_"].names["pkg_config"] = "libconfig"
        self.cpp_info.components["libconfig_"].libs = ["libconfig"]

        self.cpp_info.components["libconfig++"].names["cmake_find_package"] = "libconfig++"
        self.cpp_info.components["libconfig++"].names["cmake_find_package_multi"] = "libconfig++"
        self.cpp_info.components["libconfig++"].names["pkg_config"] = "libconfig++"
        self.cpp_info.components["libconfig++"].libs = ["libconfig++"]

        if not self.options.shared:
            self.cpp_info.components["libconfig_"].defines.append("LIBCONFIG_STATIC")
            self.cpp_info.components["libconfig++"].defines.append("LIBCONFIGXX_STATIC")
        if self.settings.os == "Windows":
            self.cpp_info.components["libconfig_"].system_libs.append("shlwapi")
            self.cpp_info.components["libconfig++"].system_libs.append("shlwapi")
