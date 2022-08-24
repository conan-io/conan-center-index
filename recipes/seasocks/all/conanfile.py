from conans import CMake, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.43.0"


class SeasocksConan(ConanFile):
    name = "seasocks"
    description = "A tiny embeddable C++ HTTP and WebSocket server for Linux"
    topics = ("seasocks", "embeddable", "webserver", "websockets")
    homepage = "https://github.com/mattgodbolt/seasocks"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-2-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
    }

    generators = "cmake", "cmake_find_package"
    exports_sources = "CMakeLists.txt"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration(f"Seasocks {self.version} doesn't support this os")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        # No warnings as errors
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(cmakelists, "-Werror", "")
        tools.replace_in_file(cmakelists, "-pedantic-errors", "")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["DEFLATE_SUPPORT"] = self.options.with_zlib
        cmake.definitions["SEASOCKS_SHARED"] = self.options.shared
        cmake.definitions["SEASOCKS_EXAMPLE_APP"] = False
        cmake.definitions["UNITTESTS"] = False
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Seasocks")
        self.cpp_info.set_property("cmake_target_name", "Seasocks::seasocks")

        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["libseasocks"].libs = ["seasocks"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libseasocks"].system_libs.append("pthread")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "Seasocks"
        self.cpp_info.names["cmake_find_package_multi"] = "Seasocks"
        self.cpp_info.components["libseasocks"].names["cmake_find_package"] = "seasocks"
        self.cpp_info.components["libseasocks"].names["cmake_find_package_multi"] = "seasocks"
        self.cpp_info.components["libseasocks"].set_property("cmake_target_name", "Seasocks::seasocks")
        if self.options.with_zlib:
            self.cpp_info.components["libseasocks"].requires = ["zlib::zlib"]
