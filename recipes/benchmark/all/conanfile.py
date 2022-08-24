from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
import os

required_conan_version = ">=1.33.0"


class BenchmarkConan(ConanFile):
    name = "benchmark"
    description = "A microbenchmark support library."
    topics = ("benchmark", "google", "microbenchmark")
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://github.com/google/benchmark"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "arch", "build_type", "compiler", "os"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_lto": [True, False],
        "enable_exceptions": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_lto": False,
        "enable_exceptions": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version.value) <= 12:
            raise ConanInvalidConfiguration("{} {} does not support Visual Studio <= 12".format(self.name, self.version))

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Windows shared builds are not supported right now, see issue #639")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        self._cmake.definitions["BENCHMARK_ENABLE_TESTING"] = "OFF"
        self._cmake.definitions["BENCHMARK_ENABLE_GTEST_TESTS"] = "OFF"
        self._cmake.definitions["BENCHMARK_ENABLE_LTO"] = "ON" if self.options.enable_lto else "OFF"
        self._cmake.definitions["BENCHMARK_ENABLE_EXCEPTIONS"] = "ON" if self.options.enable_exceptions else "OFF"

        if self.settings.os != "Windows":
            if cross_building(self):
                self._cmake.definitions["HAVE_STD_REGEX"] = False
                self._cmake.definitions["HAVE_POSIX_REGEX"] = False
                self._cmake.definitions["HAVE_STEADY_CLOCK"] = False
            self._cmake.definitions["BENCHMARK_USE_LIBCXX"] = "ON" if self.settings.compiler.get_safe("libcxx") == "libc++" else "OFF"
        else:
            self._cmake.definitions["BENCHMARK_USE_LIBCXX"] = "OFF"

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'share'))

    def package_info(self):
        self.cpp_info.libs = ["benchmark", "benchmark_main"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.extend(["pthread", "rt"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("shlwapi")
        elif self.settings.os == "SunOS":
            self.cpp_info.system_libs.append("kstat")
