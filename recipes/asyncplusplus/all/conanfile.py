import os

from conans import ConanFile, CMake, tools

class AsyncplusplusConan(ConanFile):
    name = "asyncplusplus"
    description = "Async++ concurrency framework for C++11"
    license = "MIT"
    topics = ("conan", "asyncplusplus", "async", "parallel", "task", "scheduler")
    homepage = "https://github.com/Amanieu/asyncplusplus"
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
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        # FIXME: official CMake target is exported without namespace
        self.cpp_info.names["cmake_find_package"] = "Async++"
        self.cpp_info.names["cmake_find_package_multi"] = "Async++"
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["LIBASYNC_STATIC"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
