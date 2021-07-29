from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob

required_conan_version = ">=1.28.0"


class LibRtlSdrConan(ConanFile):
    name = "librtlsdr"
    description = "Software to turn the RTL2832U into an SDR"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://osmocom.org/projects/rtl-sdr/wiki/Rtl-sdr"
    license = "GPL-2.0"
    topics = ("conan", "sdr", "rtl-sdr")
    generators = ("cmake_find_package", "pkg_config")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

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

    def requirements(self):
        self.requires("libusb/1.0.24")
        # Same rules as libusb. What's the get_safe equivalent for this?
        if self.settings.os in ["Linux", "Android"]:
            self.options["libusb"].enable_udev = True
        if self.settings.compiler == "Visual Studio":
            self.requires("pthreads4w/3.0.0")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob(self.name + "-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        # self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.configure(
            source_folder=self._source_subfolder, build_folder=self._build_subfolder
        )
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
