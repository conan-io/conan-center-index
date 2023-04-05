from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
import os

required_conan_version = ">=1.53.0"


class CpuinfoConan(ConanFile):
    name = "cpuinfo"
    description = "cpuinfo is a library to detect essential for performance " \
                  "optimization information about host CPU."
    license = "BSD-2-Clause"
    topics = ("cpu", "cpuid", "cpu-cache", "cpu-model", "instruction-set", "cpu-topology")
    homepage = "https://github.com/pytorch/cpuinfo"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "log_level": ["default", "debug", "info", "warning", "error", "fatal", "none"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "log_level": "default",
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("shared cpuinfo not supported on Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # cpuinfo
        tc.cache_variables["CPUINFO_LIBRARY_TYPE"] = "default"
        tc.cache_variables["CPUINFO_RUNTIME_TYPE"] = "default"
        tc.cache_variables["CPUINFO_LOG_LEVEL"] = self.options.log_level
        tc.variables["CPUINFO_BUILD_TOOLS"] = False
        tc.variables["CPUINFO_BUILD_UNIT_TESTS"] = False
        tc.variables["CPUINFO_BUILD_MOCK_TESTS"] = False
        tc.variables["CPUINFO_BUILD_BENCHMARKS"] = False
        # clog (always static)
        tc.cache_variables["CLOG_RUNTIME_TYPE"] = "default"
        tc.variables["CLOG_BUILD_TESTS"] = False
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                              "SET_PROPERTY(TARGET clog PROPERTY POSITION_INDEPENDENT_CODE ON)",
                              "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libcpuinfo")
        self.cpp_info.libs = ["cpuinfo", "clog"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
