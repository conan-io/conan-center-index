from conans import ConanFile, CMake, tools


class SystemcComponentsConan(ConanFile):
    name = "systemc-components"
    version = "2022.04"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    description = "<Description of SystemcComponents here>"
    topics = ("systemc", "modeling", "tracing", "tlm")
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
    generators = "cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "11")

    def source(self):
        self.run("git clone --recursive --branch develop https://github.com/Minres/SystemC-Components.git")
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
        tools.replace_in_file("SystemC-Components/CMakeLists.txt", "project(scc VERSION 2022.4.0 LANGUAGES CXX C)",
                              '''project(scc VERSION 2022.4.0 LANGUAGES CXX C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SC_WITH_PHASE_CALLBACKS"] = self.options.SC_WITH_PHASE_CALLBACKS
        cmake.definitions["SC_WITH_PHASE_CALLBACK_TRACING"] = self.options.SC_WITH_PHASE_CALLBACK_TRACING
        cmake.configure(source_folder="SystemC-Components")
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_folder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["libbusses"]

