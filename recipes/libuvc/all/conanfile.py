from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class LibuvcConan(ConanFile):
    name = "libuvc"
    description = "A cross-platform library for USB video devices"
    topics = ("libuvc", "libusb", "usb", "video")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libuvc/libuvc"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "jpeg_turbo": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "jpeg_turbo": False,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("libusb/1.0.24")
        if self.options.jpeg_turbo:
            self.requires("libjpeg-turbo/2.1.2")
        else:
            self.requires("libjpeg/9d")

    def validate(self):
        if self._is_msvc:
            # Upstream issues, e.g.:
            # https://github.com/libuvc/libuvc/issues/100
            # https://github.com/libuvc/libuvc/issues/105
            raise ConanInvalidConfiguration("libuvc is not compatible with Visual Studio.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
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
        cmake_target = "UVCShared" if self.options.shared else "UVCStatic"
        self.cpp_info.set_property("cmake_file_name", "libuvc")
        self.cpp_info.set_property("cmake_target_name", "LibUVC::{}".format(cmake_target))
        self.cpp_info.set_property("pkg_config_name", "libuvc")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["_libuvc"].libs = tools.collect_libs(self)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "libuvc"
        self.cpp_info.filenames["cmake_find_package_multi"] = "libuvc"
        self.cpp_info.names["cmake_find_package"] = "LibUVC"
        self.cpp_info.names["cmake_find_package_multi"] = "LibUVC"
        self.cpp_info.components["_libuvc"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["_libuvc"].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components["_libuvc"].set_property("cmake_target_name", "LibUVC::{}".format(cmake_target))
        self.cpp_info.components["_libuvc"].set_property("pkg_config_name", "libuvc")
        self.cpp_info.components["_libuvc"].requires = [
            "libusb::libusb",
            "libjpeg-turbo::libjpeg-turbo" if self.options.jpeg_turbo else "libjpeg::libjpeg"
        ]
