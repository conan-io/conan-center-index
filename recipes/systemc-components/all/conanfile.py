from conans import ConanFile, tools, CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os
import shutil

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
        "fPIC": [True, False],
        "SC_WITH_PHASE_CALLBACKS": [True, False],
        "SC_WITH_PHASE_CALLBACK_TRACING": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "SC_WITH_PHASE_CALLBACKS": False,
        "SC_WITH_PHASE_CALLBACK_TRACING": False
    }
    generators = "cmake", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration(
                f"{self.name} is not suppported on {self.settings.os}.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build_requirements(self):
        self.build_requires("cmake/3.16")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SC_WITH_PHASE_CALLBACKS"] = self.options.SC_WITH_PHASE_CALLBACKS
        cmake.definitions["SC_WITH_PHASE_CALLBACK_TRACING"] = self.options.SC_WITH_PHASE_CALLBACK_TRACING
        cmake.definitions["BUILD_SCC_DOCUMENTATION"] = False
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        libs = os.listdir(os.path.join(self.package_folder, "lib", "static"))
        for file_name in libs:
            shutil.move(os.path.join(self.package_folder, "lib", "static", file_name),
                        os.path.join(self.package_folder, "lib"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "static"))

    def package_info(self):
        self.cpp_info.components["busses"].libs = ["busses"]
        self.cpp_info.components["scc-sysc"].libs = ["scc-sysc"]
        self.cpp_info.components["scc-util"].libs = ["scc-util"]
        self.cpp_info.components["scv-tr"].libs = ["scv-tr"]
        self.cpp_info.components["tlm-interfaces"].libs = ["tlm-interfaces"]
