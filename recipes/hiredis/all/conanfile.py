from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


class HiredisConan(ConanFile):
    name = "hiredis"
    description = "Hiredis is a minimalistic C client library for the Redis database."
    license = "BSD-3-Clause"
    topics = ("hiredis", "redis", "client", "database")
    homepage = "https://github.com/redis/hiredis"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": False,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_ssl:
            self.requires("openssl/1.1.1q")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_SSL"] = self.options.with_ssl
        self._cmake.definitions["DISABLE_TESTS"] = True
        self._cmake.definitions["ENABLE_EXAMPLES"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "hiredis")

        # hiredis
        self.cpp_info.components["hiredislib"].set_property("cmake_target_name", "hiredis::hiredis")
        self.cpp_info.components["hiredislib"].set_property("pkg_config_name", "hiredis")
        self.cpp_info.components["hiredislib"].names["cmake_find_package"] = "hiredis"
        self.cpp_info.components["hiredislib"].names["cmake_find_package_multi"] = "hiredis"
        self.cpp_info.components["hiredislib"].libs = ["hiredis"]
        if self.settings.os == "Windows":
            self.cpp_info.components["hiredislib"].system_libs = ["ws2_32"]
        # hiredis_ssl
        if self.options.with_ssl:
            self.cpp_info.components["hiredis_ssl"].set_property("cmake_target_name", "hiredis::hiredis_ssl")
            self.cpp_info.components["hiredis_ssl"].set_property("pkg_config_name", "hiredis_ssl")
            self.cpp_info.components["hiredis_ssl"].names["cmake_find_package"] = "hiredis_ssl"
            self.cpp_info.components["hiredis_ssl"].names["cmake_find_package_multi"] = "hiredis_ssl"
            self.cpp_info.components["hiredis_ssl"].libs = ["hiredis_ssl"]
            self.cpp_info.components["hiredis_ssl"].requires = ["openssl::ssl"]
            if self.settings.os == "Windows":
                self.cpp_info.components["hiredis_ssl"].requires.append("hiredislib")

            # These cmake_target_name and pkg_config_name are unofficial. It avoids conflicts
            # in conan generators between global target/pkg-config and hiredislib component.
            # TODO: eventually remove the cmake_target_name trick if conan can implement smarter logic
            # in CMakeDeps when a downstream recipe requires another recipe globally
            # (link to all components directly instead of global target)
            self.cpp_info.set_property("cmake_target_name", "hiredis::hiredis_all_unofficial")
            self.cpp_info.set_property("pkg_config_name", "hiredis_all_unofficial")
