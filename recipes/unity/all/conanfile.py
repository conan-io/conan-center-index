from conans import ConanFile, CMake
from conans import tools
import os

class UnityConan(ConanFile):
    name = "unity"
    license = "MIT"
    url = "https://github.com/ThrowTheSwitch/Unity"
    description = "Conan wrap around unity"
    topics = ("todo")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = ["make", "cmake"]
    exports_sources = ["*"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["UNITY_EXTENSION_FIXTURE"] = "ON"
        self._cmake.definitions["UNITY_EXTENSION_MEMORY"] = "ON"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # TODO - check if we can remove this.
        self.copy("*.h", dst="include", src=(self._source_subfolder + "/src"))
        self.copy("*.h", dst="include", src=(self._source_subfolder + "/extras/fixture/src"))
        self.copy("*.h", dst="include", src=(self._source_subfolder + "/extras/memory/src"))
        self.copy("*.rb", dst="auto", src=(self._source_subfolder + "/auto"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.names["cmake_find_package"] = "unity"
        self.cpp_info.names["cmake_find_package_multi"] = "unity"
        self.cpp_info.bindirs = ['auto']
