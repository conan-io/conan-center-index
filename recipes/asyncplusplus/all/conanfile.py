from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.36.0"


class AsyncplusplusConan(ConanFile):
    name = "asyncplusplus"
    description = "Async++ concurrency framework for C++11"
    license = "MIT"
    topics = ("async", "parallel", "task", "scheduler")
    homepage = "https://github.com/Amanieu/asyncplusplus"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
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

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

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
        self.cpp_info.set_property("cmake_file_name", "Async++")
        self.cpp_info.set_property("cmake_target_name", "Async++")
        self.cpp_info.libs = ["async++"]
        if not self.options.shared:
            self.cpp_info.defines = ["LIBASYNC_STATIC"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
