from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.36.0"


class CpuinfoConan(ConanFile):
    name = "cpuinfo"
    description = "cpuinfo is a library to detect essential for performance " \
                  "optimization information about host CPU."
    license = "BSD-2-Clause"
    topics = ("cpuinfo", "cpu", "cpuid", "cpu-cache", "cpu-model",
              "instruction-set", "cpu-topology")
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

    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("shared cpuinfo not supported on Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "SET_PROPERTY(TARGET clog PROPERTY POSITION_INDEPENDENT_CODE ON)",
                              "")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        # cpuinfo
        cmake.definitions["CPUINFO_LIBRARY_TYPE"] = "default"
        cmake.definitions["CPUINFO_RUNTIME_TYPE"] = "default"
        cmake.definitions["CPUINFO_LOG_LEVEL"] = self.options.log_level
        cmake.definitions["CPUINFO_BUILD_TOOLS"] = False
        cmake.definitions["CPUINFO_BUILD_UNIT_TESTS"] = False
        cmake.definitions["CPUINFO_BUILD_MOCK_TESTS"] = False
        cmake.definitions["CPUINFO_BUILD_BENCHMARKS"] = False
        # clog (always static)
        cmake.definitions["CLOG_RUNTIME_TYPE"] = "default"
        cmake.definitions["CLOG_BUILD_TESTS"] = False
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)

        # CMAKE_SYSTEM_PROCESSOR must be manually set if cross-building
        if tools.cross_building(self):
            cmake_system_processor = {
                "armv8": "arm64",
                "armv8.3": "arm64",
            }.get(str(self.settings.arch), str(self.settings.arch))
            cmake.definitions["CONAN_CPUINFO_SYSTEM_PROCESSOR"] = cmake_system_processor

        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libcpuinfo")
        self.cpp_info.libs = ["cpuinfo", "clog"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
