from conans import ConanFile, CMake, tools
import functools
import os

required_conan_version = ">=1.43.0"


class OnigurumaConan(ConanFile):
    name = "oniguruma"
    description = "Oniguruma is a modern and flexible regular expressions library."
    license = "BSD-2-Clause"
    topics = ("oniguruma", "regex")
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

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_POSIX_API"] = self.options.posix_api
        cmake.definitions["ENABLE_BINARY_COMPATIBLE_POSIX_API"] = self.options.posix_api
        if tools.Version(self.version) >= "6.9.8":
            cmake.definitions["INSTALL_DOCUMENTATION"] = False
            cmake.definitions["INSTALL_EXAMPLES"] = False
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        if tools.Version(self.version) < "6.9.8":
            tools.rmdir(os.path.join(self.package_folder, "share"))
        else:
            if self.settings.os == "Windows" and self.options.shared:
                tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "onig-config")
            else:
                tools.rmdir(os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "oniguruma")
        self.cpp_info.set_property("cmake_target_name", "oniguruma::onig")
        self.cpp_info.set_property("pkg_config_name", "oniguruma")
        # TODO: back to global scope after conan v2 once cmake_find_package_* removed
        self.cpp_info.components["onig"].libs = ["onig"]
        if not self.options.shared:
            self.cpp_info.components["onig"].defines.append("ONIG_STATIC")

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.components["onig"].set_property("cmake_target_name", "oniguruma::onig")
        self.cpp_info.components["onig"].set_property("pkg_config_name", "oniguruma")
        self.cpp_info.components["onig"].names["cmake_find_package"] = "onig"
        self.cpp_info.components["onig"].names["cmake_find_package_multi"] = "onig"
        self.cpp_info.components["onig"].names["pkg_config"] = "oniguruma"
