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
        "enable_display": [True, False],
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
        "enable_display": False,
        "enable_xrandr": False,
        "enable_xshm": False,
    }

    no_copy_source = True

    @property
    def _cimg_defines(self):
        defines = []
        for option, define in [
            ("enable_fftw", "cimg_use_fftw3"),
            ("enable_jpeg", "cimg_use_jpeg"),
            ("enable_openexr", "cimg_use_openexr"),
            ("enable_png", "cimg_use_png"),
            ("enable_tiff", "cimg_use_tiff"),
            ("enable_ffmpeg", "cimg_use_ffmpeg"),
            ("enable_opencv", "cimg_use_opencv"),
            ("enable_magick", "cimg_use_magick"),
            ("enable_xrandr", "cimg_use_xrandr"),
            ("enable_xshm", "cimg_use_xshm"),
        ]:
            if getattr(self.options, option):
                defines.append(define)

        if not self.options.get_safe("enable_display"):
            # disable display capabilities
            defines.append("cimg_display=0")
        elif self.settings.os == "Windows":
            # use the Microsoft GDI32 framework
            defines.append("cimg_display=2")
        else:
            # use the X-Window framework (X11)
            defines.append("cimg_display=1")

        return defines

    def config_options(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            # Requires Xorg
            del self.options.enable_xrandr
            del self.options.enable_xshm
        if self.settings.os not in ["Linux", "FreeBSD", "Windows"]:
            # Must support either X11 or GDI32
            del self.options.enable_display

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.enable_fftw:
            self.requires("fftw/3.3.10")
        if self.options.enable_jpeg:
            self.requires("libjpeg/9e")
        if self.options.enable_openexr:
            self.requires("openexr/3.2.1")
            self.requires("imath/3.1.9")
        if self.options.enable_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.enable_tiff:
            self.requires("libtiff/4.6.0")
        if self.options.enable_ffmpeg:
            if self.options.enable_opencv:
                self.requires("ffmpeg/4.4.4")
            else:
                self.requires("ffmpeg/6.1")
        if self.options.enable_opencv:
            self.requires("opencv/4.8.1")
        if self.options.enable_magick:
            self.requires("imagemagick/7.0.11-14")
        if self.options.enable_display and self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xorg/system")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "11")

        if not self.options.get_safe("enable_display"):
            if self.options.enable_xrandr or self.options.enable_xshm:
                raise ConanInvalidConfiguration("X11 options enable_xrandr and enable_xshm require enable_display=True")

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
        self.cpp_info.defines = self._cimg_defines

        if self.settings.os == "Windows" and self.options.enable_display:
            self.cpp_info.system_libs.append("gdi32")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        #       do not use this name in CMakeDeps, it was a mistake, there is no official CMake config file
        self.cpp_info.names["cmake_find_package"] = "CImg"
        self.cpp_info.names["cmake_find_package_multi"] = "CImg"
