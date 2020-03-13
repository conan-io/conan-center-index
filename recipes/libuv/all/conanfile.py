from conans import ConanFile, CMake, tools
import os


class libuvConan(ConanFile):
    name = "libuv"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libuv.org"
    description = "A multi-platform support library with a focus on asynchronous I/O"
    topics = ("libuv", "asynchronous", "io", "networking", "multi-platform", "conan-recipe")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    generators = "cmake"
    exports_sources = [
        "CMakeLists.txt",
        "patches/*"
    ]

    @property
    def _source_subfolder_name(self):
        return "source_subfolder"

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self.settings.compiler == "Visual Studio":
            if tools.Version(self.settings.compiler.version) < "14":
                raise ConanInvalidConfiguration("Visual Studio 2015 or higher required")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libuv-{}".format(self.version), self._source_subfolder_name)

    def build(self):
        if "patches" in self.conan_data and self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "pthread", "rt"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["iphlpapi", "psapi", "userenv", "ws2_32"]
