from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class OnigurumaConan(ConanFile):
    name = "oniguruma"
    description = "Oniguruma is a modern and flexible regular expressions library."
    license = "BSD-2-Clause"
    topics = ("conan", "oniguruma", "regex")
    homepage = "https://github.com/kkos/oniguruma"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "posix_api": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "posix_api": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_POSIX_API"] = self.options.posix_api
        self._cmake.definitions["ENABLE_BINARY_COMPATIBLE_POSIX_API"] = self.options.posix_api
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "oniguruma"
        self.cpp_info.names["cmake_find_package_multi"] = "oniguruma"
        self.cpp_info.names["pkg_config"] = "oniguruma"
        self.cpp_info.components["onig"].names["cmake_find_package"] = "onig"
        self.cpp_info.components["onig"].names["cmake_find_package_multi"] = "onig"
        self.cpp_info.components["onig"].names["pkg_config"] = "oniguruma"
        self.cpp_info.components["onig"].libs = ["onig"]
        if not self.options.shared:
            self.cpp_info.components["onig"].defines.append("ONIG_STATIC")
