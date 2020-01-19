import os
from conans import ConanFile, CMake, tools


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

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            self.options.remove("fPIC")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['SIMDJSON_BUILD_STATIC'] = not self.options.shared
        cmake.definitions['SIMDJSON_ENABLE_THREADS'] = self.options.threads
        cmake.definitions['SIMDJSON_DISABLE_AVX'] = not self.options.avx
        cmake.definitions['SIMDJSON_SANITIZE'] = False
        cmake.definitions['ENABLE_FUZZING'] = False
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
