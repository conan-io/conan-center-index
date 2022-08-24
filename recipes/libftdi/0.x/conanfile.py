from from conan import ConanFile, tools
from conans import CMake
from contextlib import contextmanager
import os


class LibFtdi(ConanFile):
    name = "libftdi"
    description = "libFTDI - FTDI USB driver with bitbang mode"
    topics = ("conan", "libconfuse", "configuration", "parser")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.intra2net.com/en/developer/libftdi"
    license = "LGPL-2.0"
    exports_sources = "CMakeLists.txt", "patches/**"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_cpp_wrapper": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_cpp_wrapper": True,
    }
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
        if not self.options.enable_cpp_wrapper:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("libftdi-{}".format(self.version), self._source_subfolder)

    def requirements(self):
        self.requires("libusb-compat/0.1.7")
        if self.options.enable_cpp_wrapper:
            self.requires("boost/1.74.0")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FTDIPP"] = self.options.enable_cpp_wrapper
        self._cmake.definitions["PYTHON_BINDINGS"] = False
        self._cmake.definitions["EXAMPLES"] = False
        self._cmake.definitions["DOCUMENTATION"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "CMAKE_BINARY_DIR", "PROJECT_BINARY_DIR")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "CMAKE_SOURCE_DIR", "PROJECT_SOURCE_DIR")
        tools.replace_in_file(os.path.join(self._source_subfolder, "ftdipp", "CMakeLists.txt"), "CMAKE_SOURCE_DIR", "PROJECT_SOURCE_DIR")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        if self.options.enable_cpp_wrapper:
            self.cpp_info.libs.append("ftdipp")
        self.cpp_info.libs.append("ftdi")
