import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class SimdjsonConan(ConanFile):
    name = "simdjson"
    description = "Parsing gigabytes of JSON per second"
    topics = ("conan", "json", "parser", "simd", "format")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lemire/simdjson"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "threads": [True, False]}
    default_options = {'shared': False,
                       'fPIC': True,
                       'threads': True}
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
            "gcc": "7.4",
            "Visual Studio": "15.7",
            "clang": "6",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "17")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not fully support.".format(self.name))
        else:
            self.output.warn("{} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions['SIMDJSON_BUILD_STATIC'] = not self.options.shared
        self._cmake.definitions['SIMDJSON_ENABLE_THREADS'] = self.options.threads
        self._cmake.definitions['SIMDJSON_SANITIZE'] = False
        self._cmake.definitions['SIMDJSON_JUST_LIBRARY'] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.libs = ['simdjson']
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
        if self.options.threads:
            self.cpp_info.defines = ["SIMDJSON_THREADS_ENABLED=1"]
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.append("pthread")
        if self.options.shared:
            self.cpp_info.defines.append("SIMDJSON_USING_LIBRARY=1")
