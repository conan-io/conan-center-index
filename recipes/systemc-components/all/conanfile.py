from conans import ConanFile, tools, CMake
from conan.errors import ConanInvalidConfiguration

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

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration(f"{self.name} is not suppported on {self.settings.os}.")

    def source(self):
        self.run("git clone --recursive --branch develop https://github.com/Minres/SystemC-Components.git scc")
#        tools.get(**self.conan_data["sources"][self.version])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SC_WITH_PHASE_CALLBACKS"] = self.options.SC_WITH_PHASE_CALLBACKS
        cmake.definitions["SC_WITH_PHASE_CALLBACK_TRACING"] = self.options.SC_WITH_PHASE_CALLBACK_TRACING
        cmake.verbose = True
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_folder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["scc"]
