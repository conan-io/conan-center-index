import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class PerfettoConan(ConanFile):
    name = "perfetto"
    version = "20.1"
    license = "Apache-2"
    homepage = "https://perfetto.dev"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Performance instrumentation and tracing for Android, Linux and Chrome"
    topics = ("linux", "profiling")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
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
        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < 7:
            raise ConanInvalidConfiguration ("perfetto requires gcc >= 7")
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libc++":
            raise ConanInvalidConfiguration ("perfetto cannot be built with libc++ runtime")
        #if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < "16":
        #    raise ConanInvalidConfiguration("Visual Studio < 2019 not yet supported in this recipe")
        #if self.settings.compiler == "Visual Studio" and "MT" in self.settings.compiler.runtime:
        #    raise ConanInvalidConfiguration("Visual Studio build with MT runtime is not supported")
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
               strip_root=True, destination=self._source_subfolder)
        
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
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.components["libperfetto"].name = "perfetto"
        self.cpp_info.components["libperfetto"].libs = ["perfetto"]
        self.cpp_info.components["libperfetto"].names["pkgconfig"] = "libperfetto"
        if self.settings.os == "Linux":
            self.cpp_info.components["libperfetto"].system_libs.append("pthread")
        if self.settings.os == "Windows":
            self.cpp_info.components["libperfetto"].system_libs.append("ws2_32")

