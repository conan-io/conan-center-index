from conan import ConanFile
from conan.tools.scm import Version
from conan.tools.files import get
from conans import tools, CMake
from conan.errors import ConanInvalidConfiguration
import functools

required_conan_version = ">=1.43.0"

class SystemcComponentsConan(ConanFile):
    name = "scc"
    description = """A light weight productivity library for SystemC and TLM 2.0"""
    homepage = "https://minres.github.io/SystemC-Components"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    topics = ("systemc", "modeling", "tlm", "scc")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "fPIC": [True, False],
        "sc_with_phases_callbacks": [True, False],
        "sc_with_phases_callback_tracing": [True, False]
    }
    default_options = {
        "fPIC": True,
        "sc_with_phases_callbacks": False,
        "sc_with_phases_callback_tracing": False
    }
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    # no exports_sources attribute, but export_sources(self) method instead
    # this allows finer grain exportation of patches per version
    def export_sources(self):
        self.copy("CMakeLists.txt")
            
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            
    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration(f"{self.name} is not suppported on {self.settings.os}.")
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration("GCC < version 7 is not supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build_requirements(self):
        self.build_requires("cmake/3.16.2")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SC_WITH_PHASE_CALLBACKS"] = self.options.sc_with_phases_callbacks
        cmake.definitions["SC_WITH_PHASE_CALLBACK_TRACING"] = self.options.sc_with_phases_callback_tracing
        cmake.definitions["BUILD_SCC_DOCUMENTATION"] = False
        cmake.definitions["SCC_LIB_ONLY"] = True
        if self.settings.os == "Windows":
            cmake.definitions["SCC_LIMIT_TRACE_TYPE_LIST"] = True
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.components["busses"].libs = ["busses"]
        self.cpp_info.components["scc-sysc"].libs = ["scc-sysc"]
        self.cpp_info.components["scc-util"].libs = ["scc-util"]
        self.cpp_info.components["scv-tr"].libs = ["scv-tr"]
        self.cpp_info.components["tlm-interfaces"].libs = ["tlm-interfaces"]
