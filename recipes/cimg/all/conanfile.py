from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class CImgConan(ConanFile):
    name = "cimg"
    description = "The CImg Library is a small and open-source C++ toolkit for image processing"
    homepage = "http://cimg.eu"
    topics = "conan", "cimg", "physics", "simulation", "robotics", "kinematics", "engine",
    license = "CeCILL V2"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True
    settings = "compiler"

    _cimg_options = [
        ("enable_fftw",         "cimg_use_fftw",       "fftw/3.3.8"),
        ("enable_jpeg",         "cimg_use_jpeg",       "libjpeg/9d"),
        ("enable_openexr",      "cimg_use_openexr",    "openexr/2.4.0"),
        ("enable_png",          "cimg_use_png",        "libpng/1.6.37"),
        ("enable_tiff",         "cimg_use_tiff",       "libtiff/4.0.9"),
        # ("enable_ffmpeg",       "cimg_use_ffmpeg",     "ffmpeg/???"),
        # ("enable_opencv"        "cimg_use_opencv",     "opencv/???"),
        # ("enable_magick"        "cimg_use_magick",     "magick/???"),
        # ("enable_xrandr",       "cimg_use_xrandr",     "xrandr/???"),
        # ("enable_xshm",         "cimg_use_xshm",       "xshm/???"),
    ]

    options = dict((option, [True, False]) for option, _, _ in _cimg_options)
    default_options = dict((option, True) for option, _, _ in _cimg_options)

    def configure(self):
        if self.settings.compiler.cppstd and self.settings.compiler.cppstd in ("98"):
            raise ConanInvalidConfiguration("cimg requires at least c++11")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        for option, _, req in self._cimg_options:
            if getattr(self.options, option):
                self.requires(req)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("CImg-{}".format(self.version), self._source_subfolder)

    def package(self):
        self.copy("Licence*", src=self._source_subfolder, dst="licenses")
        self.copy("CImg.h", src=self._source_subfolder, dst="include")
        shutil.copytree(os.path.join(self.source_folder, self._source_subfolder, "plugins"),
                        os.path.join(self.package_folder, "include", "plugins"))

    def build(self):
        pass

    def package_id(self):
        del self.settings.compiler
        self.info.header_only()
        for option, _, _ in self._cimg_options:
            delattr(self.info.options, option)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CImg"
        self.cpp_info.names["cmake_find_package_multi"] = "CImg"

        for option, define, _ in self._cimg_options:
            if getattr(self.options, option):
                self.cpp_info.defines.append(define)
