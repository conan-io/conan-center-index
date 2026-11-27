from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.1"


class SoralogConan(ConanFile):
    name = "soralog"
    description = "Fast and flexible C++ logger with low-overhead logging calls"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xDimon/soralog"
    topics = ("logging", "logger", "log", "yaml")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # fmt and yaml-cpp types are used in public headers
        self.requires("fmt/[>=12 <13]", transitive_headers=True, transitive_libs=True)
        self.requires("yaml-cpp/[>=0.8.0 <0.10.0]", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Upstream fetches dependencies with Hunter by default
        tc.cache_variables["PACKAGE_MANAGER"] = "none"
        tc.generate()
        deps = CMakeDeps(self)
        if self.dependencies["fmt"].options.header_only:
            # Upstream links to fmt::fmt, header-only fmt is fmt::fmt-header-only
            deps.set_property("fmt", "cmake_target_aliases", ["fmt::fmt"])
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "soralog")
        self.cpp_info.set_property("cmake_target_name", "soralog::soralog_all")

        self.cpp_info.components["sink"].set_property("cmake_target_name", "soralog::sink")
        self.cpp_info.components["sink"].libs = ["sink"]
        self.cpp_info.components["sink"].requires = ["fmt::fmt"]

        self.cpp_info.components["sink_to_nowhere"].set_property("cmake_target_name", "soralog::sink_to_nowhere")
        self.cpp_info.components["sink_to_nowhere"].libs = ["sink_to_nowhere"]
        self.cpp_info.components["sink_to_nowhere"].requires = ["sink"]

        self.cpp_info.components["sink_to_console"].set_property("cmake_target_name", "soralog::sink_to_console")
        self.cpp_info.components["sink_to_console"].libs = ["sink_to_console"]
        self.cpp_info.components["sink_to_console"].requires = ["sink"]

        self.cpp_info.components["sink_to_file"].set_property("cmake_target_name", "soralog::sink_to_file")
        self.cpp_info.components["sink_to_file"].libs = ["sink_to_file"]
        self.cpp_info.components["sink_to_file"].requires = ["sink"]

        # Upstream builds the syslog sink everywhere but on Windows,
        # and the Event Log sink on Windows only
        if self.settings.os == "Windows":
            system_sink = "sink_to_eventlog"
            self.cpp_info.components["sink_to_eventlog"].system_libs = ["advapi32"]
        else:
            system_sink = "sink_to_syslog"
        self.cpp_info.components[system_sink].set_property("cmake_target_name", f"soralog::{system_sink}")
        self.cpp_info.components[system_sink].libs = [system_sink]
        self.cpp_info.components[system_sink].requires = ["sink"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["sink"].system_libs = ["pthread"]
            self.cpp_info.components["sink_to_console"].system_libs = ["pthread"]
            self.cpp_info.components["sink_to_file"].system_libs = ["pthread"]
            self.cpp_info.components[system_sink].system_libs = ["pthread"]

        self.cpp_info.components["multisink"].set_property("cmake_target_name", "soralog::multisink")
        self.cpp_info.components["multisink"].libs = ["multisink"]
        self.cpp_info.components["multisink"].requires = ["sink"]

        self.cpp_info.components["logging_system"].set_property("cmake_target_name", "soralog::logging_system")
        self.cpp_info.components["logging_system"].libs = ["logging_system"]
        self.cpp_info.components["logging_system"].requires = ["sink", "sink_to_nowhere"]

        # group, logger and configurator are header-only upstream
        self.cpp_info.components["group"].set_property("cmake_target_name", "soralog::group")
        self.cpp_info.components["group"].requires = ["logging_system"]
        self.cpp_info.components["group"].libdirs = []
        self.cpp_info.components["group"].bindirs = []

        self.cpp_info.components["logger"].set_property("cmake_target_name", "soralog::logger")
        self.cpp_info.components["logger"].requires = ["logging_system"]
        self.cpp_info.components["logger"].libdirs = []
        self.cpp_info.components["logger"].bindirs = []

        self.cpp_info.components["configurator"].set_property("cmake_target_name", "soralog::configurator")
        self.cpp_info.components["configurator"].requires = ["sink_to_nowhere", "sink_to_console", "sink_to_file",
                                                             system_sink, "multisink"]
        self.cpp_info.components["configurator"].libdirs = []
        self.cpp_info.components["configurator"].bindirs = []

        self.cpp_info.components["configurator_yaml"].set_property("cmake_target_name", "soralog::configurator_yaml")
        self.cpp_info.components["configurator_yaml"].set_property("cmake_target_aliases", ["soralog::yaml"])
        self.cpp_info.components["configurator_yaml"].libs = ["configurator_yaml"]
        self.cpp_info.components["configurator_yaml"].requires = ["yaml-cpp::yaml-cpp", "configurator", "logging_system"]

        self.cpp_info.components["fallback_configurator"].set_property("cmake_target_name", "soralog::fallback_configurator")
        self.cpp_info.components["fallback_configurator"].set_property("cmake_target_aliases", ["soralog::fallback"])
        self.cpp_info.components["fallback_configurator"].libs = ["fallback_configurator"]
        self.cpp_info.components["fallback_configurator"].requires = ["configurator", "logging_system"]

        self.cpp_info.components["soralog"].set_property("cmake_target_name", "soralog::soralog")
        self.cpp_info.components["soralog"].libs = ["soralog"]
        self.cpp_info.components["soralog"].requires = ["logging_system", "sink", "group", "configurator", "logger"]
