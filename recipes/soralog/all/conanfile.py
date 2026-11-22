from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
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

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        # std::ranges and std::views are used
        return {
            "gcc": "10",
            "clang": "15",
            "apple-clang": "15",
            "msvc": "193",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # fmt and yaml-cpp types are used in public headers
        self.requires("fmt/12.2.0", transitive_headers=True, transitive_libs=True)
        self.requires("yaml-cpp/0.9.0", transitive_headers=True, transitive_libs=True)

    def validate(self):
        # Upstream build accepts only GCC, Clang and MSVC
        if str(self.settings.compiler) not in self._compilers_minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} supports only GCC, Clang and MSVC")
        check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version[str(self.settings.compiler)]
        if Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        # Upstream links to fmt::fmt, which is not provided by header-only fmt
        if self.dependencies["fmt"].options.header_only:
            raise ConanInvalidConfiguration(f"{self.ref} requires fmt/*:header_only=False")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Upstream fetches dependencies with Hunter by default
        tc.cache_variables["PACKAGE_MANAGER"] = "none"
        tc.generate()
        deps = CMakeDeps(self)
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

        def _component(name, requires, is_library=True):
            component = self.cpp_info.components[name]
            component.set_property("cmake_target_name", f"soralog::{name}")
            component.requires = requires
            if is_library:
                component.libs = [name]
            else:
                component.libdirs = []
                component.bindirs = []
            return component

        # Upstream builds the syslog sink everywhere but on Windows,
        # and the Event Log sink on Windows only
        if self.settings.os == "Windows":
            system_sink = "sink_to_eventlog"
        else:
            system_sink = "sink_to_syslog"

        threaded = [_component("sink", ["fmt::fmt"])]
        _component("sink_to_nowhere", ["sink"])
        for name in ("sink_to_console", "sink_to_file", system_sink):
            threaded.append(_component(name, ["sink"]))
        if self.settings.os in ["Linux", "FreeBSD"]:
            for component in threaded:
                component.system_libs = ["pthread"]
        if self.settings.os == "Windows":
            self.cpp_info.components["sink_to_eventlog"].system_libs = ["advapi32"]
        _component("multisink", ["sink"])
        _component("logging_system", ["sink", "sink_to_nowhere"])
        _component("group", ["logging_system"], is_library=False)
        _component("logger", ["logging_system"], is_library=False)
        _component("configurator", ["sink_to_nowhere", "sink_to_console", "sink_to_file",
                                     system_sink, "multisink"], is_library=False)
        _component("configurator_yaml", ["yaml-cpp::yaml-cpp", "configurator", "logging_system"]) \
            .set_property("cmake_target_aliases", ["soralog::yaml"])
        _component("fallback_configurator", ["configurator", "logging_system"]) \
            .set_property("cmake_target_aliases", ["soralog::fallback"])
        _component("soralog", ["logging_system", "sink", "group", "configurator", "logger"])
