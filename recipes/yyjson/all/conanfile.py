from conan import ConanFile, tools
from conans import CMake
import os
import functools

required_conan_version = ">=1.43.0"

class YyjsonConan(ConanFile):
    name = "yyjson"
    description = "A high performance JSON library written in ANSI C."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ibireme/yyjson"
    topics = ("yyjson", "json", "serialization", "deserialization")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["yyjson"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("YYJSON_IMPORTS")

        self.cpp_info.set_property("cmake_file_name", "yyjson")
        self.cpp_info.set_property("cmake_target_name", "yyjson::yyjson")
