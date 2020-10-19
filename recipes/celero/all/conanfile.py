import os

from conans import ConanFile, CMake, tools

class CeleroConan(ConanFile):
    name = "celero"
    description = "C++ Benchmarking Library"
    license = "Apache-2.0"
    topics = ("conan", "celero", "benchmark", "benchmark-tests", "measurements", "microbenchmarks")
    homepage = "https://github.com/DigitalInBlue/Celero"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("Celero-" + self.version, self._source_subfolder)

    def _patch_sources(self):
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(cmakelists,
                              "target_compile_options(${PROJECT_NAME} PRIVATE -fPIC)",
                              "")
        tools.replace_in_file(cmakelists,
                              "ARCHIVE DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/static",
                              "ARCHIVE DESTINATION ${CMAKE_INSTALL_PREFIX}/lib")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CELERO_COMPILE_DYNAMIC_LIBRARIES"] = self.options.shared
        self._cmake.definitions["CELERO_ENABLE_EXPERIMENTS"] = False
        self._cmake.definitions["CELERO_ENABLE_FOLDERS"] = False
        self._cmake.definitions["CELERO_ENABLE_TESTS"] = False
        self._cmake.definitions["CELERO_TREAT_WARNINGS_AS_ERRORS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        # FIXME: official CMake target is exported without namespace
        self.cpp_info.names["cmake_find_package"] = "celero"
        self.cpp_info.names["cmake_find_package_multi"] = "celero"
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["CELERO_STATIC"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["PowrProf"]
