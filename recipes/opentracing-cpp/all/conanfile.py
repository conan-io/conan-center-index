import os

from conans import ConanFile, CMake, tools

class OpenTracingConan(ConanFile):
    name = "opentracing-cpp"
    description = "C++ implementation of the OpenTracing API http://opentracing.io"
    license = "Apache-2.0"
    topics = ("conan", "opentracing")
    homepage = "https://github.com/opentracing/opentracing-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_mocktracer": [True, False],
        "enable_dynamic_load": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_mocktracer": False,
        "enable_dynamic_load": True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_MOCKTRACER"] = self.options.enable_mocktracer
        self._cmake.definitions["BUILD_DYNAMIC_LOADING"] = self.options.enable_dynamic_load
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["ENABLE_LINTING"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "OpenTracing"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenTracing"

        if self.options.shared:
            self.cpp_info.components["opentracing"].names["cmake_find_package"] = "opentracing"
            self.cpp_info.components["opentracing"].names["cmake_find_package_multi"] = "opentracing"
            self.cpp_info.components["opentracing"].libs = ["opentracing"]
        else:
            self.cpp_info.components["opentracing-static"].names["cmake_find_package"] = "opentracing-static"
            self.cpp_info.components["opentracing-static"].names["cmake_find_package_multi"] = "opentracing-static"
            self.cpp_info.components["opentracing-static"].libs = ["opentracing-static"]
            self.cpp_info.components["opentracing-static"].defines.append('OPENTRACING_STATIC')
