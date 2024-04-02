from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.51.1"


class CImgConan(ConanFile):
    name = "cimg"
    description = "The CImg Library is a small and open-source C++ toolkit for image processing"
    license = "CeCILL V2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://cimg.eu"
    topics = ("physics", "simulation", "robotics", "kinematics", "engine")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_fftw": [True, False],
        "enable_jpeg": [True, False],
        "enable_openexr": [True, False],
        "enable_png": [True, False],
        "enable_tiff": [True, False],
        "enable_ffmpeg": [True, False],
        "enable_opencv": [True, False],
        "enable_magick": [True, False],
        "enable_xrandr": [True, False],
        "enable_xshm": [True, False],
    }
    default_options = {
        "enable_fftw": False,
        "enable_jpeg": False,
        "enable_openexr": False,
        "enable_png": False,
        "enable_tiff": False,
        "enable_ffmpeg": False,
        "enable_opencv": False,
        "enable_magick": False,
        "enable_xrandr": False,
        "enable_xshm": False,
    }

    no_copy_source = True

    @property
    def _cimg_defines(self):
        return [
            ("enable_fftw",    "cimg_use_fftw"),
            ("enable_jpeg",    "cimg_use_jpeg"),
            ("enable_openexr", "cimg_use_openexr"),
            ("enable_png",     "cimg_use_png"),
            ("enable_tiff",    "cimg_use_tiff"),
            ("enable_ffmpeg",  "cimg_use_ffmpeg"),
            ("enable_opencv",  "cimg_use_opencv"),
            ("enable_magick",  "cimg_use_magick"),
            ("enable_xrandr",  "cimg_use_xrandr"),
            ("enable_xshm",    "cimg_use_xshm"),
        ]

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.enable_fftw:
            self.requires("fftw/3.3.10")
        if self.options.enable_jpeg:
            self.requires("libjpeg/9e")
        if self.options.enable_openexr:
            self.requires("openexr/3.2.1")
        if self.options.enable_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.enable_tiff:
            self.requires("libtiff/4.6.0")
        if self.options.enable_ffmpeg:
            if self.options.enable_opencv:
                self.requires("ffmpeg/4.4")
            else:
                self.requires("ffmpeg/5.1")
        if self.options.enable_opencv:
            self.requires("opencv/4.5.5")
        if self.options.enable_magick:
            self.requires("imagemagick/7.0.11-14")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "11")
        # TODO: Update requirements when available in CCI
        if self.options.enable_xrandr:
            raise ConanInvalidConfiguration("xrandr not available in CCI yet")
        if self.options.enable_xshm:
            raise ConanInvalidConfiguration("xshm not available in CCI yet")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "Licence*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "CImg.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        copy(self, "*", os.path.join(self.source_folder, "plugins"),
                        os.path.join(self.package_folder, "include", "plugins"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "CImg")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        for option, define in self._cimg_defines:
            if getattr(self.options, option):
                self.cpp_info.defines.append(define)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        #       do not use this name in CMakeDeps, it was a mistake, there is no offical CMake config file
        self.cpp_info.names["cmake_find_package"] = "CImg"
        self.cpp_info.names["cmake_find_package_multi"] = "CImg"
