from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import glob


class CppBenchmark(ConanFile):
    name = "cppbenchmark"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/chronoxor/CppBenchmark"
    description = "Performance benchmark framework for C++ with nanoseconds measure precision."
    topics = ("conan", "utils", "library", "benchmark")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False}
    requires = ["hdrhistogram-c/0.11.1", "cpp-optparse/cci.20171104"]
    generators = "cmake"
    exports_sources = ["patches/**", "CMakeLists.txt"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": 10,
            "clang": 6,
            "gcc": 7,
            "Visual Studio": 16,
        }

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["CPPBENCHMARK_MODULE"] = "OFF"
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("CppBenchmark-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, self, "17")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.scm.Version(self, self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("cppbenchmark requires C++17, which your compiler does not support.")
        else:
            self.output.warn("cppbenchmark requires C++17. Your compiler is unknown. Assuming it supports C++17.")

    def build(self):
        self._patch()

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self, self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
