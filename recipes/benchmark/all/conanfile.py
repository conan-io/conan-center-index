from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class BenchmarkConan(ConanFile):
    name = "benchmark"
    description = "A microbenchmark support library."
    topics = ("conan", "benchmark", "google", "microbenchmark")
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
        "enable_exceptions": [True, False]
    }
    default_options = {"shared": False, "fPIC": True, "enable_lto": False, "enable_exceptions": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version.value) <= 12:
                raise ConanInvalidConfiguration("{} {} does not support Visual Studio <= 12".format(self.name, self.version))
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Windows shared builds are not supported right now, see issue #639")

    def _configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["BENCHMARK_ENABLE_TESTING"] = "OFF"
        cmake.definitions["BENCHMARK_ENABLE_GTEST_TESTS"] = "OFF"
        cmake.definitions["BENCHMARK_ENABLE_LTO"] = "ON" if self.options.enable_lto else "OFF"
        cmake.definitions["BENCHMARK_ENABLE_EXCEPTIONS"] = "ON" if self.options.enable_exceptions else "OFF"

        # See https://github.com/google/benchmark/pull/638 for Windows 32 build explanation
        if self.settings.os != "Windows":
            cmake.definitions["BENCHMARK_BUILD_32_BITS"] = "ON" if "64" not in str(self.settings.arch) else "OFF"
            cmake.definitions["BENCHMARK_USE_LIBCXX"] = "ON" if (str(self.settings.compiler.libcxx) == "libc++") else "OFF"
        else:
            cmake.definitions["BENCHMARK_USE_LIBCXX"] = "OFF"

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread", "rt"])
        elif self.settings.os == "Windows":
            self.cpp_info.libs.append("shlwapi")
        elif self.settings.os == "SunOS":
            self.cpp_info.libs.append("kstat")
