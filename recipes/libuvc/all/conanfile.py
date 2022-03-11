import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class LibuvcConan(ConanFile):
    name = "libuvc"
    description = "A cross-platform library for USB video devices"
    topics = ("conan", "libuvc", "libusb", "usb", "video")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libuvc/libuvc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "jpeg_turbo": [True, False]}
    default_options = {"shared": False, "fPIC": True, "jpeg_turbo": False}
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "patches/*"]
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.compiler == "Visual Studio":
            # Upstream issues, e.g.:
            # https://github.com/libuvc/libuvc/issues/100
            # https://github.com/libuvc/libuvc/issues/105
            raise ConanInvalidConfiguration("libuvc is not compatible with Visual Studio.")
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libusb/1.0.24")
        if self.options.jpeg_turbo:
            self.requires("libjpeg-turbo/2.1.0")
        else:
            self.requires("libjpeg/9d")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["CMAKE_BUILD_TARGET"] = "Shared" if self.options.shared else "Static"
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "libuvc"
        self.cpp_info.filenames["cmake_find_package_multi"] = "libuvc"
        self.cpp_info.names["cmake_find_package"] = "LibUVC"
        self.cpp_info.names["cmake_find_package_multi"] = "LibUVC"
        self.cpp_info.names["pkg_config"] = "libuvc"
        cmake_target = "UVCShared" if self.options.shared else "UVCStatic"
        self.cpp_info.components["_libuvc"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["_libuvc"].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components["_libuvc"].names["pkg_config"] = "libuvc"
        self.cpp_info.components["_libuvc"].libs = tools.collect_libs(self)
        self.cpp_info.components["_libuvc"].requires = [
            "libusb::libusb",
            "libjpeg-turbo::libjpeg-turbo" if self.options.jpeg_turbo else "libjpeg::libjpeg"
        ]
