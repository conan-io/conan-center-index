from conans import CMake
from conan import ConanFile
from conan.tools import scm, build, files
from conan.errors import ConanInvalidConfiguration
import os
import glob


class CpploggingConan(ConanFile):
    name = "cpplogging"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/chronoxor/CppLogging"
    description = "C++ Logging Library provides functionality to log different events with a high" \
        " throughput in multithreaded environment into different sinks (console, files, rolling files," \
        " syslog, etc.). Logging configuration is very flexible and gives functionality to build flexible"\
        " logger hierarchy with combination of logging processors (sync, async), filters, layouts (binary,"\
        " hash, text) and appenders."
    topics = ("performance", "logging", "speed", "logging-library", "low-latency")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False}
    generators = "cmake", "cmake_find_package"
    exports_sources = ["patches/**", "CMakeLists.txt"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["CPPLOGGING_MODULE"] = "OFF"
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "15",
            "clang": "5",
            "apple-clang": "10",
        }

    def requirements(self):
        self.requires("zlib/1.2.13")
        if self.version < "1.0.3.0" :
            self.requires("cppcommon/1.0.2.0")
        else:
            self.requires("cppcommon/1.0.3.0")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            build.check_min_cppstd(self, "17")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)

        if not minimum_version:
            self.output.warn("cpplogging requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif scm.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("cpplogging requires a compiler that supports at least C++17")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("CppLogging-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            files.patch(self, **patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy(pattern="*.inl", dst="include", src=os.path.join(self._source_subfolder, "include"))

    def package_info(self):
        self.cpp_info.libs = files.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "crypt32", "mswsock"]
