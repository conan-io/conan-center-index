import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class SimdjsonConan(ConanFile):
    name = "simdjson"
    version = '0.4.7'
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
    def _supported_cppstd(self):
        return ["11", "gnu11","14", "gnu14", "17", "gnu17", "20", "gnu20"]

    def _is_supported_compiler(self):
        # Other compilers might work, but these are the compilers that are actively supported, tested.
        # Results with other compilers are unpredictable.
        supported_compilers = [("apple-clang", 10), ("clang", 6), ("gcc", 7), ("Visual Studio", 15.7)]
        compiler, version = self.settings.compiler, Version(self.settings.compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def configure(self):
        if self.settings.compiler == "Visual Studio":
            del self.options.fPIC
        if self.settings.compiler.cppstd and \
           not self.settings.compiler.cppstd in self._supported_cppstd:
          raise ConanInvalidConfiguration("This library requires c++11 standard or higher."
                                          " {} required."
                                          .format(self.settings.compiler.cppstd))

        if not self._is_supported_compiler():
            raise ConanInvalidConfiguration("This library is tested with a family of recent compilers."
                                            " {} {} is not supported."
                                            .format(self.settings.compiler, self.settings.compiler.version))
   
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if(self._cmake):
                return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions['SIMDJSON_BUILD_STATIC'] = not self.options.shared
        self._cmake.definitions['SIMDJSON_ENABLE_THREADS'] = self.options.threads
        self._cmake.definitions['SIMDJSON_SANITIZE'] = False
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

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
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]



