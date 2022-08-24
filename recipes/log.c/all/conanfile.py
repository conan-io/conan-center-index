from conan import ConanFile, tools
from conan.tools.cmake import CMake
import glob


class logcConan(ConanFile):
    name = "log.c"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rxi/log.c"
    description = "A simple logging library implemented in C99"
    topics = ("logging", "log", "logging-library", "conan", "logc", "purec", "c99")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "color": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "color": True}
    generators = "cmake"
    exports_sources = ["CMakeLists.txt",
                       "patches/*"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        tools.rename(glob.glob(self.name + "-*/")[0], self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["COLOR"] = self.options.color
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

