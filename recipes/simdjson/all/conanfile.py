import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class SimdjsonConan(ConanFile):
    name = "simdjson"
    description = "Parsing gigabytes of JSON per second"
    topics = ("conan", "json", "parser", "simd", "format")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "Ahttps://github.com/lemire/simdjson"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "threads": [True, False],
               "avx": [True, False]}
    default_options = {'shared': False,
                       'fPIC': True,
                       'threads': True,
                       'avx': True}
    _source_subfolder = "source_subfolder"

    @property
    def _supported_cppstd(self):
        return ["17", "gnu17", "20", "gnu20"]

    def _has_support_for_cpp17(self):
        supported_compilers = [("apple-clang", 10), ("clang", 6), ("gcc", 7), ("Visual Studio", 15.7)]
        compiler, version = self.settings.compiler, Version(self.settings.compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            self.options.remove("fPIC")
        if self.settings.compiler.cppstd and \
           not self.settings.compiler.cppstd in self._supported_cppstd:
          raise ConanInvalidConfiguration("This library requires c++17 standard or higher."
                                          " {} required."
                                          .format(self.settings.compiler.cppstd))

        if not self._has_support_for_cpp17():
            raise ConanInvalidConfiguration("This library requires C++17 or higher support standard."
                                            " {} {} is not supported."
                                            .format(self.settings.compiler, self.settings.compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        # In version 0.2.1 CMAKE_CXX_FLAGS are ignored
        tools.replace_in_file(os.path.join(self._source_subfolder, 'tools', 'cmake', 'FindOptions.cmake'),
                              'set(CMAKE_CXX_FLAGS "${CXXSTD_FLAGS}',
                              'set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${CXXSTD_FLAGS}',
                              strict=False)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['SIMDJSON_BUILD_STATIC'] = not self.options.shared
        cmake.definitions['SIMDJSON_ENABLE_THREADS'] = self.options.threads
        cmake.definitions['SIMDJSON_DISABLE_AVX'] = not self.options.avx
        cmake.definitions['SIMDJSON_SANITIZE'] = False
        cmake.definitions['ENABLE_FUZZING'] = False
        cmake.verbose = True
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        # remove unneeded directories
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

        self.copy("license", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['simdjson']
