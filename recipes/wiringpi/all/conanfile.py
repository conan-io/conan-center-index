from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class WiringpiConan(ConanFile):
    name = "wiringpi"
    license = "LGPL-3.0"
    description = "GPIO Interface library for the Raspberry Pi"
    homepage = "http://wiringpi.com"
    topics = ("wiringpi", "gpio", "raspberrypi")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "wpi_extensions": [True, False],
               "with_devlib": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "wpi_extensions": False,
                       "with_devlib": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("{} only works for Linux.".format(self.name))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_WPI_EXTENSIONS"] = self.options.wpi_extensions
        self._cmake.definitions["WITH_DEV_LIB"] = self.options.with_devlib
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["wiringPi"]
        if self.options.with_devlib:
            self.cpp_info.libs.append("wiringPiDevLib")
        if self.options.wpi_extensions:
            self.cpp_info.libs.append("crypt")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "m", "rt"]
