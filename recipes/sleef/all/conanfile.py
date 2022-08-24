from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.32.0"


class SleefConan(ConanFile):
    name = "sleef"
    description = "SLEEF is a library that implements vectorized versions " \
                  "of C standard math functions."
    license = "BSL-1.0"
    topics = ("conan", "sleef", "vectorization", "simd")
    homepage = "https://sleef.org"
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

    short_paths = True

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("shared sleef not supported on Windows, it produces runtime errors")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_STATIC_TEST_BINS"] = False
        self._cmake.definitions["ENABLE_LTO"] = False
        self._cmake.definitions["BUILD_LIBM"] = True
        self._cmake.definitions["BUILD_DFT"] = False
        self._cmake.definitions["BUILD_QUAD"] = False
        self._cmake.definitions["BUILD_GNUABI_LIBS"] = False
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_INLINE_HEADERS"] = False
        self._cmake.definitions["SLEEF_TEST_ALL_IUT"] = False
        self._cmake.definitions["SLEEF_SHOW_CONFIG"] = True
        self._cmake.definitions["SLEEF_SHOW_ERROR_LOG"] = False
        self._cmake.definitions["ENFORCE_TESTER"] = False
        self._cmake.definitions["ENFORCE_TESTER3"] = False
        self._cmake.definitions["ENABLE_ALTDIV"] = False
        self._cmake.definitions["ENABLE_ALTSQRT"] = False
        self._cmake.definitions["DISABLE_FFTW"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "sleef"
        self.cpp_info.libs = ["sleef"]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines = ["SLEEF_STATIC_LIBS"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
