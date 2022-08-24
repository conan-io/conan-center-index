from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.36.0"


class CImgConan(ConanFile):
    name = "cimg"
    description = "The CImg Library is a small and open-source C++ toolkit for image processing"
    homepage = "http://cimg.eu"
    topics = ("cimg", "physics", "simulation", "robotics", "kinematics", "engine")
    license = "CeCILL V2"
    url = "https://github.com/conan-io/conan-center-index"

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
        "enable_fftw": True,
        "enable_jpeg": True,
        "enable_openexr": True,
        "enable_png": True,
        "enable_tiff": True,
        "enable_ffmpeg": True,
        "enable_opencv": True,
        "enable_magick": False,
        "enable_xrandr": False,
        "enable_xshm": False,
    }

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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

    def requirements(self):
        if self.options.enable_fftw:
            self.requires("fftw/3.3.9")
        if self.options.enable_jpeg:
            self.requires("libjpeg/9d")
        if self.options.enable_openexr:
            self.requires("openexr/2.5.7")
        if self.options.enable_png:
            self.requires("libpng/1.6.37")
        if self.options.enable_tiff:
            self.requires("libtiff/4.3.0")
        if self.options.enable_ffmpeg:
            self.requires("ffmpeg/4.4")
        if self.options.enable_opencv:
            self.requires("opencv/4.5.3")
        if self.options.enable_magick:
            self.requires("imagemagick/7.0.11-14")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, "11")
        # TODO: Update requirements when available in CCI
        if self.options.enable_xrandr:
            raise ConanInvalidConfiguration("xrandr not available in CCI yet")
        if self.options.enable_xshm:
            raise ConanInvalidConfiguration("xshm not available in CCI yet")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("Licence*", src=self._source_subfolder, dst="licenses")
        self.copy("CImg.h", src=self._source_subfolder, dst="include")
        shutil.copytree(os.path.join(self.source_folder, self._source_subfolder, "plugins"),
                        os.path.join(self.package_folder, "include", "plugins"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "CImg")
        for option, define in self._cimg_defines:
            if getattr(self.options, option):
                self.cpp_info.defines.append(define)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        #       do not use this name in CMakeDeps, it was a mistake, there is no offical CMake config file
        self.cpp_info.names["cmake_find_package"] = "CImg"
        self.cpp_info.names["cmake_find_package_multi"] = "CImg"
        self.cpp_info.names["pkg_config"] = "CImg"
