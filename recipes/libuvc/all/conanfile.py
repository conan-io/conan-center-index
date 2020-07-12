import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class LibuvcConan(ConanFile):
    name = "libuvc"
    description = "A cross-platform library for USB video devices"
    topics = ("conan", "libuvc", "libusb", "usb", "video")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libuvc/libuvc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "jpeg_turbo": [True, False]}
    default_options = {"shared": False, "fPIC": True, "jpeg_turbo": False}
    generators = "cmake_find_package"
    requires = "libusb/1.0.23"
    exports_sources = ["CMakeLists.txt"]

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.compiler == "Visual Studio":
            # Upstream issues, e.g.:
            # https://github.com/libuvc/libuvc/issues/100
            # https://github.com/libuvc/libuvc/issues/105
            raise ConanInvalidConfiguration("This library is not compatible with Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)


    def requirements(self):
        if self.options.jpeg_turbo:
            self.requires("libjpeg-turbo/2.0.4")
        else:
            self.requires("libjpeg/9d")

    def build(self):
        _cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(_cmakelists, "pkg_check_modules(LIBUSB libusb-1.0)", "find_package(libusb REQUIRED)")
        tools.replace_in_file(_cmakelists, "${LIBUSB_INCLUDE_DIRS}", "${libusb_INCLUDE_DIRS}")

        cmake = CMake(self)
        if self.options.shared:
            _cmake_defs = {"CMAKE_BUILD_TARGET" : "Shared" }
        else:
            _cmake_defs = {"CMAKE_BUILD_TARGET" : "Static" }
        cmake.configure(defs = _cmake_defs, source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.h", dst="include", src=os.path.join(self._build_subfolder, "include"))
        if self.options.shared:
            self.copy("libuvc.so", dst="lib", src=self._build_subfolder, keep_path=False)
        else:
            self.copy("libuvc.a", dst="lib", src=self._build_subfolder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
