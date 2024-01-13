from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.1"


class CImgConan(ConanFile):
    name = "cimg"
    description = "The CImg Library is a small and open-source C++ toolkit for image processing"
    license = "CeCILL V2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://cimg.eu"
    topics = ("image", "image-processing", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "enable_curl": [True, False],
        "enable_display": [True, False],
        "enable_ffmpeg": [True, False],
        "enable_fftw": [True, False],
        "enable_heif": [True, False],
        "enable_jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg", True, False],
        "enable_magick": [True, False],
        "enable_opencv": [True, False],
        "enable_openexr": [True, False],
        "enable_openmp": [True, False],
        "enable_png": [True, False],
        "enable_tiff": [True, False],
        "enable_tinyexr": [True, False],
        "enable_xrandr": [True, False],
        "enable_xshm": [True, False],
        "enable_zlib": [True, False],
    }
    default_options = {
        "enable_curl": False,
        "enable_display": False,
        "enable_ffmpeg": False,
        "enable_fftw": False,
        "enable_heif": False,
        "enable_jpeg": "libjpeg",
        "enable_magick": False,
        "enable_opencv": False,
        "enable_openexr": False,
        "enable_openmp": False,
        "enable_png": False,
        "enable_tiff": False,
        "enable_tinyexr": False,
        "enable_xrandr": False,
        "enable_xshm": False,
        "enable_zlib": False,
    }
    options_description = {
        # "enable_board": "Support drawing of 3D objects in a vector-graphics canvas, using libboard",
        "enable_curl": "Add support for downloading files from the network, using libcurl",
        "enable_display": "Enable display capabilities of CImg, using either X11 or GDI32",
        "enable_ffmpeg": "Add support for various video files, using the FFMPEG library",
        "enable_fftw": "Enable faster Discrete Fourier Transform computation, using the FFTW3 library",
        "enable_heif": "Support HEIF (.heic and .avif) image files, using libheif",
        "enable_jpeg": "Support JPEG (.jpg) image files, using the JPEG library",
        # "enable_lapack": "Enable the use of LAPACK routines for matrix computations",
        "enable_magick": "Add support of most classical image file formats, using the Magick++ library",
        # "enable_minc2": "Support MINC2 (.mnc) image files, using the MINC2 library",
        "enable_opencv": "Enable OpenCV support",
        "enable_openexr": "Add support for EXR (.exr) image files, using the OpenEXR library",
        "enable_openmp": "Enable OpenMP support",
        "enable_png": "Support PNG (.png) image files, using the PNG library",
        "enable_tiff": "Support TIFF (.tiff) image files, using the TIFF library",
        "enable_tinyexr": "Support EXR (.exr) image files, using the TinyEXR library",
        "enable_xrandr": "Enable screen mode switching, using the XRandr library (when using X11)",
        "enable_xshm": "Enable fast image display, using the XSHM library (when using X11)",
        "enable_zlib": "Support compressed .cimgz files, using the ZLib library",
    }

    no_copy_source = True

    @property
    def _cimg_defines(self):
        # Based on https://github.com/GreycLab/CImg/blob/master/examples/Makefile
        defines = []
        for option, define in [
            ("enable_curl", "cimg_use_curl"),
            ("enable_ffmpeg", "cimg_use_ffmpeg"),
            ("enable_fftw", "cimg_use_fftw3"),
            ("enable_heif", "cimg_use_heif"),
            ("enable_jpeg", "cimg_use_jpeg"),
            ("enable_magick", "cimg_use_magick"),
            ("enable_opencv", "cimg_use_opencv"),
            ("enable_openexr", "cimg_use_openexr"),
            ("enable_openmp", "cimg_use_openmp"),
            ("enable_png", "cimg_use_png"),
            ("enable_tiff", "cimg_use_tiff"),
            ("enable_tinyexr", "cimg_use_tinyexr"),
            ("enable_xrandr", "cimg_use_xrandr"),
            ("enable_zlib", "cimg_use_zlib"),
            # TODO:
            # ("enable_minc2", "cimg_use_minc2"),
            # ("enable_lapack", "cimg_use_lapack"),
            # ("enable_board", "cimg_use_board"),
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

        if self.options.enable_fftw:
            if not self.dependencies["fftw"].options.threads:
                defines.append("cimg_use_fftw3_singlethread")

        return defines

    def config_options(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            # Requires Xorg
            # Also,
            # xshm: "Seems to randomly crash when used on MacOS and 64bits systems, so use it only when necessary"
            # xrandr: "Not supported by the X11 server on MacOS, so do not use it on MacOS"
            del self.options.enable_xrandr
            del self.options.enable_xshm
        if self.settings.os not in ["Linux", "FreeBSD", "Windows"]:
            # Must support either X11 or GDI32
            del self.options.enable_display
        if Version(self.version) < "2.9.7":
            del self.options.enable_heif

    def configure(self):
        # Required component in OpenCV 4.x for cv::VideoCapture and cv::VideoWriter
        self.options["opencv"].videoio = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.enable_fftw:
            self.requires("fftw/3.3.10")
        if self.options.enable_jpeg == "libjpeg" or self.options.enable_jpeg.value is True:
            self.requires("libjpeg/9e")
        elif self.options.enable_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.1")
        elif self.options.enable_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.5")
        if self.options.enable_openexr:
            self.requires("openexr/3.2.1")
            self.requires("imath/3.1.9")
        if self.options.enable_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.enable_tiff:
            self.requires("libtiff/4.6.0")
        if self.options.enable_ffmpeg:
            self.requires("ffmpeg/6.1")
        if self.options.enable_opencv:
            # FIXME: OpenCV 4.x fails to link ffmpeg libraries correctly
            self.requires("opencv/3.4.20")
        if self.options.enable_magick:
            self.requires("imagemagick/7.0.11-14")
        if self.options.enable_display and self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("xorg/system")
        if self.options.enable_openmp and self.settings.compiler in ["clang", "apple-clang"]:
            self.requires("llvm-openmp/17.0.6")
        if self.options.enable_heif:
            self.requires("libheif/1.16.2")
        if self.options.enable_zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.enable_curl:
            self.requires("libcurl/[>=7.78.0 <9]")
        if self.options.enable_tinyexr:
            self.requires("tinyexr/1.0.7")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "11")

        if not self.options.get_safe("enable_display"):
            if self.options.enable_xrandr or self.options.enable_xshm:
                raise ConanInvalidConfiguration("X11 options enable_xrandr and enable_xshm require enable_display=True")

        if self.options.enable_tinyexr:
            if self.options.enable_openexr:
                raise ConanInvalidConfiguration("OpenEXR and TinyEXR cannot be enabled simultaneously")
            if self.options.enable_zlib:
                # The miniz dependency of TinyEXR conflicts with ZLib
                # error: conflicting declaration ‘typedef void* const voidpc’
                raise ConanInvalidConfiguration("TinyEXR and ZLib cannot be enabled simultaneously due to conflicting typedefs")

        if self.options.enable_opencv and Version(self.dependencies["opencv"].ref.version) >= "4.0":
            if not self.dependencies["opencv"].options.videoio:
                raise ConanInvalidConfiguration("OpenCV must be built with videoio=True")

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

        # List specific requirements to avoid overlinking
        # Based on https://github.com/GreycLab/CImg/blob/v.3.3.3/examples/Makefile#L166-L310
        requires = []
        if self.options.enable_fftw:
            requires.append("fftw::fftw")
        if self.options.enable_jpeg == "libjpeg" or self.options.enable_jpeg.value is True:
            requires.append("libjpeg::libjpeg")
        elif self.options.enable_jpeg == "libjpeg-turbo":
            requires.append("libjpeg-turbo::jpeg")
        elif self.options.enable_jpeg == "mozjpeg":
            requires.append("mozjpeg::libjpeg")
        if self.options.enable_openexr:
            requires.append("openexr::openexr_openexr")
            requires.append("imath::imath_lib")
        if self.options.enable_png:
            requires.append("libpng::libpng")
        if self.options.enable_tiff:
            requires.append("libtiff::libtiff")
        if self.options.enable_opencv:
            requires.append("opencv::opencv_core")
            requires.append("opencv::opencv_highgui")
            if Version(self.dependencies["opencv"].ref.version) >= "4.0":
                requires.append("opencv::opencv_videoio")
        if self.options.enable_ffmpeg:
            requires.append("ffmpeg::avcodec")
            requires.append("ffmpeg::avformat")
            requires.append("ffmpeg::swscale")
        if self.options.enable_magick:
            requires.append("imagemagick::Magick++")
        if self.options.enable_display and self.settings.os in ["Linux", "FreeBSD"]:
            requires.append("xorg::x11")
            if self.options.enable_xrandr:
                requires.append("xorg::xrandr")
            if self.options.enable_xshm:
                requires.append("xorg::xext")
        if self.options.enable_openmp and self.settings.compiler in ["clang", "apple-clang"]:
            requires.append("llvm-openmp::llvm-openmp")
        if self.options.enable_heif:
            requires.append("libheif::libheif")
        if self.options.enable_zlib:
            requires.append("zlib::zlib")
        if self.options.enable_curl:
            requires.append("libcurl::libcurl")
        if self.options.enable_tinyexr:
            requires.append("tinyexr::tinyexr")
        self.cpp_info.requires = requires

        if self.settings.os == "Windows" and self.options.enable_display:
            self.cpp_info.system_libs.append("gdi32")

        if self.options.enable_openmp:
            openmp_flags = []
            if self.settings.compiler in ("clang", "apple-clang"):
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]
            elif self.settings.compiler == "gcc":
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler == "intel-cc":
                openmp_flags = ["/Qopenmp"] if self.settings.os == "Windows" else ["-Qopenmp"]
            elif is_msvc(self):
                openmp_flags = ["-openmp"]
            self.cpp_info.cflags = openmp_flags
            self.cpp_info.cxxflags = openmp_flags
            self.cpp_info.sharedlinkflags = openmp_flags
            self.cpp_info.exelinkflags = openmp_flags

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        #       do not use this name in CMakeDeps, it was a mistake, there is no official CMake config file
        self.cpp_info.names["cmake_find_package"] = "CImg"
        self.cpp_info.names["cmake_find_package_multi"] = "CImg"
