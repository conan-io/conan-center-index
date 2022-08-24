from conan import ConanFile, tools
from conans import CMake
import os
import glob
import shutil


class LibfreenectConan(ConanFile):
    name = "libfreenect"
    license = ("Apache-2.0", "GPL-2.0")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/OpenKinect/libfreenect"
    description = "Drivers and libraries for the Xbox Kinect device."
    topics = ("usb", "camera", "kinect")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
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
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("libusb/1.0.24")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_REDIST_PACKAGE"] = True
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_FAKENECT"] = False
        self._cmake.definitions["BUILD_C_SYNC"] = False
        self._cmake.definitions["BUILD_CPP"] = False
        self._cmake.definitions["BUILD_CV"] = False
        self._cmake.definitions["BUILD_AS3_SERVER"] = False
        self._cmake.definitions["BUILD_PYTHON"] = False
        self._cmake.definitions["BUILD_PYTHON2"] = False
        self._cmake.definitions["BUILD_PYTHON3"] = False
        self._cmake.definitions["BUILD_OPENNI2_DRIVER"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("APACHE20", src=self._source_subfolder, dst="licenses", keep_path=False)
        self.copy("GPL", src=self._source_subfolder, dst="licenses", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libfreenect"
        self.cpp_info.libs = ["freenect"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
