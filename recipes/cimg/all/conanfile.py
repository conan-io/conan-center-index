from conans import ConanFile, tools
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
    no_copy_source = True
    settings = "os", "arch", "compiler", "build_type"

    _cimg_options = (
        ("enable_fftw",         "cimg_use_fftw",       "fftw/3.3.9"),
        ("enable_jpeg",         "cimg_use_jpeg",       "libjpeg/9d"),
        ("enable_openexr",      "cimg_use_openexr",    "openexr/2.5.7"),
        ("enable_png",          "cimg_use_png",        "libpng/1.6.37"),
        ("enable_tiff",         "cimg_use_tiff",       "libtiff/4.3.0"),
        # ("enable_ffmpeg",       "cimg_use_ffmpeg",     "ffmpeg/???"),
        ("enable_opencv",        "cimg_use_opencv",     "opencv/4.5.3"),
        # ("enable_magick",        "cimg_use_magick",     "magick/???"),
        # ("enable_xrandr",       "cimg_use_xrandr",     "xrandr/???"),
        # ("enable_xshm",         "cimg_use_xshm",       "xshm/???"),
    )
    # TODO: Update requirements when available in CCI

    options = dict((option, [True, False]) for option, _, _ in _cimg_options)
    default_options = dict((option, True) for option, _, _ in _cimg_options)

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        for option, _, req in self._cimg_options:
            if getattr(self.options, option):
                self.requires(req)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "11")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("Licence*", src=self._source_subfolder, dst="licenses")
        self.copy("CImg.h", src=self._source_subfolder, dst="include")
        shutil.copytree(os.path.join(self.source_folder, self._source_subfolder, "plugins"),
                        os.path.join(self.package_folder, "include", "plugins"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_file", "CImg")
        for option, define, _ in self._cimg_options:
            if getattr(self.options, option):
                self.cpp_info.defines.append(define)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        #       do not use this name in CMakeDeps, it was a mistake, there is no offial config file
        self.cpp_info.names["cmake_find_package"] = "CImg"
        self.cpp_info.names["cmake_find_package_multi"] = "CImg"
