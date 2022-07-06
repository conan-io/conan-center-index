from conans import tools, CMake
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
import functools


required_conan_version = ">=1.43.0"


class SystemcComponentsConan(ConanFile):
    name = "systemc-components"
    description = """A light weight productivity library for SystemC and TLM 2.0"""
    homepage = "https://minres.github.io/SystemC-Components"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    topics = ("systemc", "modeling", "tlm", "scc")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    generators = "cmake", "cmake_find_package_multi"

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("systemc/2.3.3")
        self.requires("systemc-cci/1.0.0")
        self.requires("doxygen/1.9.4")
        self.requires("fmt/8.0.1")

    def validate(self):
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration(f"{self.name} is not suppported on {self.settings.os}.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("NOTICE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["scc"]
