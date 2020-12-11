import os
import glob
from conans import ConanFile, tools, CMake


class LibRealSenseConan(ConanFile):
    name = "librealsense"
    description = "Cross-platform library for Intel RealSense depth cameras (D400 series and the SR300) " \
                  "and the T265 tracking camera."
    homepage = "https://github.com/IntelRealSense/librealsense"
    topics = "conan", "intel", "3d", "computer vision", "robotics"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openmp": [True, False]
    }
    default_options = {"shared": False, "fPIC": True, "with_openmp": False}
    generators = ["cmake", "cmake_find_package"]
    requires = ["lz4/1.9.3", "boost/1.69.0"]

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
        if self.options.with_openmp:
            self.output.warn(
                "Conan package for openmp is not available, this package will be used from system."
            )

    def requirements(self):
        if self.settings.os != "Windows":
            self.requires("libusb/1.0.23")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("librealsense*")[0], self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self, parallel=False)
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_GLSL_EXTENSIONS"] = False
        self._cmake.definitions["BUILD_WITH_OPENMP"] = self.options.with_openmp
        self._cmake.definitions["BUILD_UNIT_TESTS"] = False
        self._cmake.definitions["BUILD_NETWORK_DEVICE"] = False
        if self.settings.os != "Macos":
            self._cmake.definitions["BUILD_WITH_TM2"] = False
            self._cmake.definitions["IMPORT_DEPTH_CAM_FW"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
