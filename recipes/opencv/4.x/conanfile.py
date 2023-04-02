from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run, check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, rename, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import re
import textwrap

required_conan_version = ">=1.54.0"


OPENCV_MAIN_MODULES_OPTIONS = (
    "calib3d",
    "dnn",
    "features2d",
    "flann",
    "gapi",
    "highgui",
    "imgcodecs",
    "imgproc",
    "ml",
    "objdetect",
    "photo",
    "stitching",
    "video",
    "videoio",
)

OPENCV_EXTRA_MODULES_OPTIONS = (
    "alphamat",
    "aruco",
    "barcode",
    "bgsegm",
    "bioinspired",
    "ccalib",
    "cudaarithm",
    "cudabgsegm",
    "cudacodec",
    "cudafeatures2d",
    "cudafilters",
    "cudaimgproc",
    "cudalegacy",
    "cudaobjdetect",
    "cudaoptflow",
    "cudastereo",
    "cudawarping",
    "cvv",
    "datasets",
    "dnn_objdetect",
    "dnn_superres",
    "dpm",
    "face",
    "freetype",
    "fuzzy",
    "hdf",
    "hfs",
    "img_hash",
    "intensity_transform",
    "line_descriptor",
    "mcc",
    "optflow",
    "ovis",
    "phase_unwrapping",
    "plot",
    "quality",
    "rapid",
    "reg",
    "rgbd",
    "saliency",
    "sfm",
    "shape",
    "stereo",
    "structured_light",
    "superres",
    "surface_matching",
    "text",
    "tracking",
    "videostab",
    "viz",
    "wechat_qrcode",
    "xfeatures2d",
    "ximgproc",
    "xobjdetect",
    "xphoto",
)

class OpenCVConan(ConanFile):
    name = "opencv"
    license = "Apache-2.0"
    homepage = "https://opencv.org"
    description = "OpenCV (Open Source Computer Vision Library)"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("computer-vision", "deep-learning", "image-processing")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        # global options
        "parallel": [False, "tbb", "openmp"],
        "with_ipp": [False, "intel-ipp", "opencv-icv"],
        "with_eigen": [True, False],
        "neon": [True, False],
        "with_opencl": [True, False],
        "with_cuda": [True, False],
        "with_cublas": [True, False],
        "with_cufft": [True, False],
        "with_cudnn": [True, False],
        "cuda_arch_bin": [None, "ANY"],
        "cpu_baseline": [None, "ANY"],
        "cpu_dispatch": [None, "ANY"],
        "world": [True, False],
        "nonfree": [True, False],
        # dnn module options
        "with_vulkan": [True, False],
        "dnn_cuda": [True, False],
        # highgui module options
        "with_gtk": [True, False],
        "with_qt": [True, False],
        # imgcodecs module options
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo", "mozjpeg"],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_jpeg2000": [False, "jasper", "openjpeg"],
        "with_openexr": [True, False],
        "with_webp": [True, False],
        "with_gdal": [True, False],
        "with_gdcm": [True, False],
        "with_imgcodec_hdr": [True, False],
        "with_imgcodec_pfm": [True, False],
        "with_imgcodec_pxm": [True, False],
        "with_imgcodec_sunraster": [True, False],
        "with_msmf": [True, False],
        "with_msmf_dxva": [True, False],
        # objdetect module options
        "with_quirc": [True, False],
        # videoio module options
        "with_ffmpeg": [True, False],
        "with_v4l": [True, False],
        # text module options
        "with_tesseract": [True, False],
        # TODO: deprecated options to remove in few months
        "contrib": [True, False, "deprecated"],
        "contrib_freetype": [True, False, "deprecated"],
        "contrib_sfm": [True, False, "deprecated"],
        "with_ade": [True, False, "deprecated"],
    }
    options.update({_name: [True, False] for _name in OPENCV_MAIN_MODULES_OPTIONS})
    options.update({_name: [True, False] for _name in OPENCV_EXTRA_MODULES_OPTIONS})

    default_options = {
        "shared": False,
        "fPIC": True,
        # global options
        "parallel": False,
        "with_ipp": False,
        "with_eigen": True,
        "neon": True,
        "with_opencl": False,
        "with_cuda": False,
        "with_cublas": False,
        "with_cufft": False,
        "with_cudnn": False,
        "cuda_arch_bin": None,
        "cpu_baseline": None,
        "cpu_dispatch": None,
        "world": False,
        "nonfree": False,
        # dnn module options
        "with_vulkan": False,
        "dnn_cuda": False,
        # highgui module options
        "with_gtk": True,
        "with_qt": False,
        # imgcodecs module options
        "with_jpeg": "libjpeg",
        "with_png": True,
        "with_tiff": True,
        "with_jpeg2000": "jasper",
        "with_openexr": True,
        "with_webp": True,
        "with_gdal": False,
        "with_gdcm": False,
        "with_imgcodec_hdr": False,
        "with_imgcodec_pfm": False,
        "with_imgcodec_pxm": False,
        "with_imgcodec_sunraster": False,
        "with_msmf": True,
        "with_msmf_dxva": True,
        # objdetect module options
        "with_quirc": True,
        # videoio module options
        "with_ffmpeg": True,
        "with_v4l": False,
        # text module options
        "with_tesseract": True,
        # TODO: deprecated options to remove in few months
        "contrib": "deprecated",
        "contrib_freetype": "deprecated",
        "contrib_sfm": "deprecated",
        "with_ade": "deprecated",
    }
    default_options.update({_name: True for _name in OPENCV_MAIN_MODULES_OPTIONS})
    default_options.update({_name: False for _name in OPENCV_EXTRA_MODULES_OPTIONS})

    short_paths = True

    @property
    def _contrib_folder(self):
        return os.path.join(self.source_folder, "contrib")

    @property
    def _has_with_jpeg2000_option(self):
        return self.settings.os != "iOS"

    @property
    def _has_with_tiff_option(self):
        return self.settings.os != "iOS"

    @property
    def _has_with_ffmpeg_option(self):
        return self.settings.os != "iOS" and self.settings.os != "WindowsStore"

    @property
    def _has_superres_option(self):
        return self.settings.os != "iOS"

    @property
    def _has_alphamat_option(self):
        return Version(self.version) >= "4.3.0"

    @property
    def _has_intensity_transform_option(self):
        return Version(self.version) >= "4.3.0"

    @property
    def _has_rapid_option(self):
        return Version(self.version) >= "4.3.0"

    @property
    def _has_mcc_option(self):
        return Version(self.version) >= "4.5.0"

    @property
    def _has_wechat_qrcode_option(self):
        return Version(self.version) >= "4.5.2"

    @property
    def _has_barcode_option(self):
        return Version(self.version) >= "4.5.3"

    @property
    def _protobuf_version(self):
        return "3.21.9"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_gtk
            del self.options.with_v4l
        if self.settings.os in ["iOS", "Android"]:
            del self.options.with_opencl
        if self.settings.os != "Windows":
            del self.options.with_msmf
            del self.options.with_msmf_dxva

        if self._has_with_ffmpeg_option:
            # Following the packager choice, ffmpeg is enabled by default when
            # supported, except on Android. See
            # https://github.com/opencv/opencv/blob/39c3334147ec02761b117f180c9c4518be18d1fa/CMakeLists.txt#L266-L268
            self.options.with_ffmpeg = self.settings.os != "Android"
        else:
            del self.options.with_ffmpeg

        if "arm" not in self.settings.arch:
            del self.options.neon
        if not self._has_with_jpeg2000_option:
            del self.options.with_jpeg2000
        if not self._has_with_tiff_option:
            del self.options.with_tiff
        if not self._has_superres_option:
            del self.options.superres
        if not self._has_alphamat_option:
            del self.options.alphamat
        if not self._has_intensity_transform_option:
            del self.options.intensity_transform
        if not self._has_rapid_option:
            del self.options.rapid
        if not self._has_mcc_option:
            del self.options.mcc
        if not self._has_wechat_qrcode_option:
            del self.options.wechat_qrcode
        if not self._has_barcode_option:
            del self.options.barcode

    @property
    def _opencv_modules(self):
        def imageformats_deps():
            components = []
            if self.options.get_safe("with_jpeg2000"):
                components.append("{0}::{0}".format(self.options.with_jpeg2000))
            if self.options.get_safe("with_png"):
                components.append("libpng::libpng")
            if self.options.get_safe("with_jpeg") == "libjpeg":
                components.append("libjpeg::libjpeg")
            elif self.options.get_safe("with_jpeg") == "libjpeg-turbo":
                components.append("libjpeg-turbo::jpeg")
            elif self.options.get_safe("with_jpeg") == "mozjpeg":
                components.append("mozjpeg::libjpeg")
            if self.options.get_safe("with_tiff"):
                components.append("libtiff::libtiff")
            if self.options.get_safe("with_openexr"):
                components.append("openexr::openexr")
            if self.options.get_safe("with_webp"):
                components.append("libwebp::libwebp")
            if self.options.get_safe("with_gdal"):
                components.append("gdal::gdal")
            if self.options.get_safe("with_gdcm"):
                components.append("gdcm::gdcm")
            return components

        def eigen():
            return ["eigen::eigen"] if self.options.with_eigen else []

        def ffmpeg():
            if self.options.get_safe("with_ffmpeg"):
                return [
                    "ffmpeg::avcodec", "ffmpeg::avdevice", "ffmpeg::avformat",
                    "ffmpeg::avutil", "ffmpeg::swscale",
                ]
            return []

        def freetype():
            return ["freetype::freetype"] if self.options.freetype else []

        def gtk():
            return ["gtk::gtk"] if self.options.get_safe("with_gtk") else []

        def ipp():
            if self.options.with_ipp == "intel-ipp":
                return ["intel-ipp::intel-ipp"]
            elif self.options.with_ipp == "opencv-icv" and not self.options.shared:
                return ["ippiw"]
            return []

        def parallel():
            return ["onetbb::onetbb"] if self.options.parallel == "tbb" else []

        def qt():
            return ["qt::qt"] if self.options.get_safe("with_qt") else []

        def quirc():
            return ["quirc::quirc"] if self.options.get_safe("with_quirc") else []

        def tesseract():
            return ["tesseract::tesseract"] if self.options.get_safe("with_tesseract") else []

        def vulkan():
            return ["vulkan-headers::vulkan-headers"] if self.options.get_safe("with_vulkan") else []

        def opencv_calib3d():
            return ["opencv_calib3d"] if self.options.calib3d else []

        def opencv_cudaarithm():
            return ["opencv_cudaarithm"] if self.options.cudaarithm else []

        def opencv_cudacodec():
            return ["opencv_cudacodec"] if self.options.cudacodec else []

        def opencv_cudafeatures2d():
            return ["opencv_cudafeatures2d"] if self.options.cudafeatures2d else []

        def opencv_cudafilters():
            return ["opencv_cudafilters"] if self.options.cudafilters else []

        def opencv_cudaimgproc():
            return ["opencv_cudaimgproc"] if self.options.cudaimgproc else []

        def opencv_cudalegacy():
            return ["opencv_cudalegacy"] if self.options.cudalegacy else []

        def opencv_cudaoptflow():
            return ["opencv_cudaoptflow"] if self.options.cudaoptflow else []

        def opencv_cudawarping():
            return ["opencv_cudawarping"] if self.options.cudawarping else []

        def opencv_dnn():
            return ["opencv_dnn"] if self.options.dnn else []

        def opencv_flann():
            return ["opencv_flann"] if self.options.flann else []

        def opencv_imgcodecs():
            return ["opencv_imgcodecs"] if self.options.imgcodecs else []

        def opencv_imgproc():
            return ["opencv_imgproc"] if self.options.imgproc else []

        def opencv_objdetect():
            return ["opencv_objdetect"] if self.options.objdetect else []

        def opencv_video():
            return ["opencv_video"] if self.options.video else []

        def opencv_videoio():
            return ["opencv_videoio"] if self.options.videoio else []

        def opencv_xfeatures2d():
            return ["opencv_xfeatures2d"] if self.options.xfeatures2d else []

        opencv_modules = {
            # Main modules
            "calib3d": {
                "is_built": self.options.calib3d,
                "mandatory_options": ["features2d", "flann", "imgproc"],
                "requires": ["opencv_core", "opencv_features2d", "opencv_flann", "opencv_imgproc"] + eigen() + ipp(),
            },
            "core": {
                "is_built": True,
                "no_option": True,
                "requires": ["zlib::zlib"] + parallel() + eigen() + ipp(),
                "system_libs": [
                    (self.settings.os == "Android", ["dl", "m", "log"]),
                    (self.settings.os == "FreeBSD", ["m", "pthread"]),
                    (self.settings.os == "Linux", ["dl", "m", "pthread", "rt"]),
                ],
                "frameworks": [
                    (self.settings.os == "Macos" and self.options.get_safe("with_opencl"), ["OpenCL"]),
                ],
            },
            "dnn": {
                "is_built": self.options.dnn,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_core", "opencv_imgproc", "protobuf::protobuf"] + vulkan() + ipp(),
            },
            "features2d": {
                "is_built": self.options.features2d,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_imgproc"] + opencv_flann() + eigen() + ipp(),
            },
            "flann": {
                "is_built": self.options.flann,
                "requires": ["opencv_core"] + ipp(),
            },
            "gapi": {
                "is_built": self.options.gapi,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_imgproc", "ade::ade"],
                "system_libs": [
                    (self.settings.os == "Windows", ["ws2_32", "wsock32"]),
                ],
            },
            "highgui": {
                "is_built": self.options.highgui,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_core", "opencv_imgproc"] + opencv_imgcodecs() +
                            opencv_videoio() + freetype() + gtk() + qt() + ipp(),
                "system_libs": [
                    (self.settings.os == "Windows", ["comctl32", "gdi32", "ole32", "setupapi", "ws2_32", "vfw32"]),
                ],
                "frameworks": [
                    (self.settings.os == "Macos", ["Cocoa"]),
                ],
            },
            "imgcodecs": {
                "is_built": self.options.imgcodecs,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_imgproc", "zlib::zlib"] + imageformats_deps() + ipp(),
                "frameworks": [
                    (is_apple_os(self), ["CoreFoundation", "CoreGraphics"]),
                    (self.settings.os == "iOS", ["UIKit"]),
                    (self.settings.os == "Macos", ["AppKit"]),
                ],
            },
            "imgproc": {
                "is_built": self.options.imgproc,
                "requires": ["opencv_core"] + ipp(),
            },
            "ml": {
                "is_built": self.options.ml,
                "requires": ["opencv_core"] + ipp(),
            },
            "objdetect": {
                "is_built": self.options.objdetect,
                "mandatory_options": ["calib3d", "imgproc"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_imgproc"] + quirc() + ipp(),
            },
            "photo": {
                "is_built": self.options.photo,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_imgproc"] + opencv_cudaarithm() + opencv_cudaimgproc() + ipp(),
            },
            "stitching": {
                "is_built": self.options.stitching,
                "mandatory_options": ["calib3d", "features2d", "flann", "imgproc"],
                "requires": ["opencv_calib3d", "opencv_features2d", "opencv_flann", "opencv_imgproc"] +
                            opencv_xfeatures2d() + opencv_cudaarithm() + opencv_cudawarping() +
                            opencv_cudafeatures2d() + opencv_cudalegacy() + opencv_cudaimgproc() + eigen() + ipp(),
            },
            "video": {
                "is_built": self.options.video,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_imgproc"] + opencv_calib3d() + ipp(),
            },
            "videoio": {
                "is_built": self.options.videoio,
                "mandatory_options": ["imgcodecs", "imgproc"],
                "requires": ["opencv_imgcodecs", "opencv_imgproc"] + ffmpeg() + ipp(),
                "system_libs": [
                    (self.settings.os == "Android" and int(str(self.settings.os.api_level)) > 20, ["mediandk"]),
                ],
                "frameworks": [
                    (is_apple_os(self), ["Accelerate", "AVFoundation", "CoreGraphics", "CoreMedia", "CoreVideo", "QuartzCore"]),
                    (self.settings.os == "iOS", ["CoreImage", "UIKit"]),
                    (self.settings.os == "Macos", ["Cocoa"]),
                ],
            },
            # Extra modules
            "alphamat": {
                "is_built": self.options.get_safe("alphamat"),
                "mandatory_options": ["with_eigen", "imgproc"],
                "requires": ["opencv_core", "opencv_imgproc"] + ipp(),
            },
            "aruco": {
                "is_built": self.options.aruco,
                "mandatory_options": ["calib3d", "imgproc"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_imgproc"] + ipp(),
            },
            "barcode": {
                "is_built": self.options.get_safe("barcode"),
                "mandatory_options": ["dnn", "imgproc"],
                "requires": ["opencv_core", "opencv_dnn", "opencv_imgproc"] + ipp(),
            },
            "bgsegm": {
                "is_built": self.options.bgsegm,
                "mandatory_options": ["calib3d", "imgproc", "video"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_imgproc", "opencv_video"] + ipp(),
            },
            "bioinspired": {
                "is_built": self.options.bioinspired,
                "requires": ["opencv_core"] + ipp(),
            },
            "ccalib": {
                "is_built": self.options.ccalib,
                "mandatory_options": ["calib3d", "features2d", "highgui", "imgproc"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_features2d", "opencv_highgui", "opencv_imgproc"] + ipp(),
            },
            "cudaarithm": {
                "is_built": self.options.cudaarithm,
                "mandatory_options": ["with_cuda"],
                "requires": ["opencv_core", "opencv_cudev"] + ipp(),
            },
            "cudabgsegm": {
                "is_built": self.options.cudabgsegm,
                "mandatory_options": ["with_cuda", "video"],
                "requires": ["opencv_video"] + ipp(),
            },
            "cudacodec": {
                "is_built": self.options.cudacodec,
                "mandatory_options": ["with_cuda", "videoio"],
                "requires": ["opencv_core", "opencv_videio", "opencv_cudev"] + ipp(),
            },
            "cudafeatures2d": {
                "is_built": self.options.cudafeatures2d,
                "mandatory_options": ["with_cuda", "features2d", "cudafilters", "cudawarping"],
                "requires": ["opencv_features2d", "opencv_cudafilters", "opencv_cudawarping"] + ipp(),
            },
            "cudafilters": {
                "is_built": self.options.cudafilters,
                "mandatory_options": ["with_cuda", "imgproc", "cudaarithm"],
                "requires": ["opencv_imgproc", "opencv_cudaarithm"] + ipp(),
            },
            "cudaimgproc": {
                "is_built": self.options.cudaimgproc,
                "mandatory_options": ["with_cuda", "imgproc"],
                "requires": ["opencv_imgproc", "opencv_cudev"] + opencv_cudaarithm() + opencv_cudafilters() + ipp(),
            },
            "cudalegacy": {
                "is_built": self.options.cudalegacy,
                "mandatory_options": ["with_cuda", "video"],
                "requires": ["opencv_core", "opencv_video"] + opencv_calib3d() + opencv_imgproc() + opencv_objdetect() +
                            opencv_cudaarithm() + opencv_cudafilters() + opencv_cudaimgproc() + ipp(),
            },
            "cudaobjdetect": {
                "is_built": self.options.cudaobjdetect,
                "mandatory_options": ["with_cuda", "objdetect", "cudaarithm", "cudawarping"],
                "requires": ["opencv_objdetect", "opencv_cudaarithm", "opencv_cudawarping"] + opencv_cudalegacy() + ipp(),
            },
            "cudaoptflow": {
                "is_built": self.options.cudaoptflow,
                "mandatory_options": ["with_cuda", "video", "cudaarithm", "cudaimgproc", "cudawarping", "optflow"],
                "requires": ["opencv_video", "opencv_cudaarithm", "cudaimgproc", "opencv_cudawarping",
                             "opencv_optflow"] + opencv_cudalegacy() + ipp(),
            },
            "cudastereo": {
                "is_built": self.options.cudastereo,
                "mandatory_options": ["with_cuda", "calib3d"],
                "requires": ["opencv_calib3d", "opencv_cudev"] + ipp(),
            },
            "cudawarping": {
                "is_built": self.options.cudawarping,
                "mandatory_options": ["with_cuda", "imgproc"],
                "requires": ["opencv_core", "opencv_imgproc", "opencv_cudev"] + ipp(),
            },
            "cudev": {
                "is_built": self.options.with_cuda,
                "no_option": True,
                "requires": ipp(),
            },
            "cvv": {
                "is_built": self.options.cvv,
                "mandatory_options": ["with_qt", "features2d", "imgproc"],
                "requires": ["opencv_core", "opencv_features2d", "opencv_imgproc", "qt::qt"] + ipp(),
            },
            "datasets": {
                "is_built": self.options.datasets,
                "mandatory_options": ["flann", "imgcodecs", "ml"],
                "requires": ["opencv_core", "opencv_flann", "opencv_imgcodecs", "opencv_ml"] + ipp(),
            },
            "dnn_objdetect": {
                "is_built": self.options.dnn_objdetect,
                "mandatory_options": ["dnn", "imgproc"],
                "requires": ["opencv_core", "opencv_dnn", "opencv_imgproc"] + ipp(),
            },
            "dnn_superres": {
                "is_built": self.options.dnn_superres,
                "mandatory_options": ["dnn", "imgproc"],
                "requires": ["opencv_core", "opencv_dnn", "opencv_imgproc"] + ipp(),
            },
            "dpm": {
                "is_built": self.options.dpm,
                "mandatory_options": ["imgproc", "objdetect"],
                "requires": ["opencv_core", "opencv_imgproc", "opencv_objdetect"] + ipp(),
            },
            "face": {
                "is_built": self.options.face,
                "mandatory_options": ["calib3d", "imgproc", "objdetect", "photo"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_imgproc", "opencv_objdetect", "opencv_photo"] + ipp(),
            },
            "freetype": {
                "is_built": self.options.freetype,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_core", "opencv_imgproc", "freetype::freetype", "harfbuzz::harfbuzz"] + ipp(),
            },
            "fuzzy": {
                "is_built": self.options.fuzzy,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_core", "opencv_imgproc"] + ipp(),
            },
            "hdf": {
                "is_built": self.options.hdf,
                "requires": ["opencv_core", "hdf5::hdf5"] + ipp(),
            },
            "hfs": {
                "is_built": self.options.hfs,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_core", "opencv_imgproc"] + ipp(),
            },
            "img_hash": {
                "is_built": self.options.img_hash,
                "is_part_of_world": False,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_core", "opencv_imgproc"] + ipp(),
            },
            "intensity_transform": {
                "is_built": self.options.get_safe("intensity_transform"),
                "requires": ["opencv_core"] + ipp(),
            },
            "line_descriptor": {
                "is_built": self.options.line_descriptor,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_imgproc"] + ipp(),
            },
            "mcc": {
                "is_built": self.options.get_safe("mcc"),
                "mandatory_options": ["calib3d", "dnn", "imgproc"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_dnn", "opencv_imgproc"] + ipp(),
            },
            "optflow": {
                "is_built": self.options.optflow,
                "mandatory_options": ["calib3d", "flann", "imgcodecs", "imgproc", "video", "ximgproc"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_flann", "opencv_imgcodecs", "opencv_imgproc",
                             "opencv_video", "opencv_ximgproc"] + ipp(),
            },
            "ovis": {
                "is_built": self.options.ovis,
                "mandatory_options": ["calib3d", "imgproc"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_imgproc", "ogre::ogre"] + ipp(),
            },
            "phase_unwrapping": {
                "is_built": self.options.phase_unwrapping,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_core", "opencv_imgproc"] + ipp(),
            },
            "plot": {
                "is_built": self.options.plot,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_core", "opencv_imgproc"] + ipp(),
            },
            "quality": {
                "is_built": self.options.quality,
                "mandatory_options": ["imgproc", "ml"],
                "requires": ["opencv_core", "opencv_imgproc", "opencv_ml"] + ipp(),
            },
            "rapid": {
                "is_built": self.options.get_safe("rapid"),
                "mandatory_options": ["calib3d", "imgproc"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_imgproc"] + ipp(),
            },
            "reg": {
                "is_built": self.options.reg,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_core", "opencv_imgproc"] + ipp(),
            },
            "rgbd": {
                "is_built": self.options.rgbd,
                "mandatory_options": ["calib3d", "imgproc"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_imgproc"] + eigen() + ipp(),
            },
            "saliency": {
                "is_built": self.options.saliency,
                "mandatory_options": ["features2d", "imgproc"],
                "requires": ["opencv_features2d", "opencv_imgproc"] + ipp(),
            },
            "sfm": {
                "is_built": self.options.sfm,
                "is_part_of_world": False,
                "mandatory_options": ["with_eigen", "calib3d", "features2d", "imgcodecs", "xfeatures2d"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_features2d", "opencv_imgcodecs", "opencv_xfeatures2d",
                             "correspondence", "multiview", "numeric", "glog::glog", "gflags::gflags"] + eigen() + ipp(),
            },
            "shape": {
                "is_built": self.options.shape,
                "mandatory_options": ["calib3d", "imgproc"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_imgproc"] + ipp(),
            },
            "stereo": {
                "is_built": self.options.stereo,
                "mandatory_options": ["features2d", "imgproc", "tracking"],
                "requires": ["opencv_core", "opencv_features2d", "opencv_imgproc", "opencv_tracking"] + ipp(),
            },
            "structured_light": {
                "is_built": self.options.structured_light,
                "mandatory_options": ["calib3d", "imgproc", "phase_unwrapping"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_imgproc", "opencv_phase_unwrapping"] + ipp(),
            },
            "superres": {
                "is_built": self.options.get_safe("superres"),
                "mandatory_options": ["imgproc", "video", "optflow"],
                "requires": ["opencv_imgproc", "opencv_video", "opencv_optflow"] + opencv_videoio() + ipp() +
                            opencv_cudaarithm() + opencv_cudafilters() + opencv_cudawarping() + opencv_cudaimgproc() +
                            opencv_cudaoptflow() + opencv_cudacodec(),
            },
            "surface_matching": {
                "is_built": self.options.surface_matching,
                "mandatory_options": ["flann"],
                "requires": ["opencv_core", "opencv_flann"] + ipp(),
            },
            "text": {
                "is_built": self.options.text,
                "mandatory_options": ["dnn", "features2d", "imgproc", "ml"],
                "requires": ["opencv_core", "opencv_dnn", "opencv_features2d", "opencv_imgproc", "opencv_ml"] +
                            tesseract() + ipp(),
            },
            "tracking": {
                "is_built": self.options.tracking,
                "mandatory_options": ["imgproc", "video"],
                "requires": ["opencv_core", "opencv_imgproc", "opencv_video"] + opencv_dnn() + ipp(),
            },
            "videostab": {
                "is_built": self.options.videostab,
                "mandatory_options": ["calib3d", "features2d", "imgproc", "photo", "video"],
                "requires": ["opencv_calib3d", "opencv_features2d", "opencv_imgproc", "opencv_photo", "opencv_video"] +
                            opencv_videoio() + ipp() + opencv_cudawarping() + opencv_cudaoptflow(),
            },
            "viz": {
                "is_built": self.options.viz,
                "requires": ["opencv_core", "vtk::vtk"] + ipp(),
            },
            "wechat_qrcode": {
                "is_built": self.options.get_safe("wechat_qrcode"),
                "mandatory_options": ["dnn", "imgproc"],
                "requires": ["opencv_core", "opencv_dnn", "opencv_imgproc"] + ipp(),
            },
            "xfeatures2d": {
                "is_built": self.options.xfeatures2d,
                "mandatory_options": ["calib3d", "features2d", "imgproc"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_features2d", "opencv_imgproc"] + ipp() + opencv_cudaarithm(),
            },
            "ximgproc": {
                "is_built": self.options.ximgproc,
                "mandatory_options": ["calib3d", "imgcodecs", "imgproc", "video"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_imgcodecs", "opencv_imgproc", "opencv_video"] +
                            eigen() + ipp(),
            },
            "xobjdetect": {
                "is_built": self.options.xobjdetect,
                "mandatory_options": ["imgcodecs", "imgproc", "objdetect"],
                "requires": ["opencv_core", "opencv_imgcodecs", "opencv_imgproc", "opencv_objdetect"] + ipp(),
            },
            "xphoto": {
                "is_built": self.options.xphoto,
                "mandatory_options": ["imgproc", "photo"],
                "requires": ["opencv_core", "opencv_imgproc", "opencv_photo"] + ipp(),
            },
            # Extra targets (without prefix in their target & lib name)
            "ippiw": {
                "is_built": self.options.with_ipp == "opencv-icv" and not self.options.shared,
                "is_part_of_world": False,
                "no_option": True,
            },
            "numeric": {
                "is_built": self.options.sfm,
                "is_part_of_world": False,
                "no_option": True,
                "requires": eigen() + ipp(),
            },
            "correspondence": {
                "is_built": self.options.sfm,
                "is_part_of_world": False,
                "no_option": True,
                "requires": ["opencv_imgcodecs", "multiview", "glog::glog"] + eigen() + ipp(),
            },
            "multiview": {
                "is_built": self.options.sfm,
                "is_part_of_world": False,
                "no_option": True,
                "requires": ["numeric", "glog::glog"] + eigen() + ipp(),
            },
        }

        if Version(self.version) >= "4.3.0":
            opencv_modules["gapi"].setdefault("requires", []).extend(opencv_video())
        if Version(self.version) >= "4.5.2":
            opencv_modules["gapi"].setdefault("requires", []).extend(opencv_calib3d())
        if Version(self.version) >= "4.5.4":
            opencv_modules["objdetect"].setdefault("requires", []).extend(opencv_dnn())
        if Version(self.version) >= "4.5.1":
            opencv_modules["video"].setdefault("requires", []).extend(opencv_dnn())
        if Version(self.version) >= "4.4.0":
            opencv_modules["intensity_transform"].setdefault("mandatory_options", []).append("imgproc")
            opencv_modules["intensity_transform"].setdefault("requires", []).append("opencv_imgproc")
        if Version(self.version) < "4.3.0":
            opencv_modules["stereo"].setdefault("mandatory_options", []).extend(["calib3d", "video"])
            opencv_modules["stereo"].setdefault("requires", []).extend(["opencv_calib3d", "opencv_video"])

        return opencv_modules

    def _get_mandatory_disabled_options(self, opencv_modules):
        direct_options_to_enable = {}
        transitive_options_to_enable = {}

        # Check which direct options have to be enabled
        base_options = [option for option, values in opencv_modules.items()
                        if not values.get("no_option") and self.options.get_safe(option)]
        for base_option in base_options:
            for mandatory_option in opencv_modules.get(base_option, {}).get("mandatory_options", []):
                if not self.options.get_safe(mandatory_option):
                    direct_options_to_enable.setdefault(mandatory_option, set()).add(base_option)

        # Now traverse the graph to check which transitive options have to be enabled
        def collect_transitive_options(base_option, option):
            for mandatory_option in opencv_modules.get(option, {}).get("mandatory_options", []):
                if not self.options.get_safe(mandatory_option):
                    if mandatory_option not in transitive_options_to_enable:
                        transitive_options_to_enable[mandatory_option] = set()
                        collect_transitive_options(base_option, mandatory_option)
                    if base_option not in direct_options_to_enable.get(mandatory_option, set()):
                        transitive_options_to_enable[mandatory_option].add(base_option)

        for base_option in base_options:
            collect_transitive_options(base_option, base_option)

        return {
            "direct": direct_options_to_enable,
            "transitive": transitive_options_to_enable,
        }

    def _solve_internal_dependency_graph(self, opencv_modules):
        disabled_options = self._get_mandatory_disabled_options(opencv_modules)
        direct_options_to_enable = disabled_options["direct"]
        transitive_options_to_enable = disabled_options["transitive"]

        # Enable mandatory options
        all_options_to_enable = set(direct_options_to_enable.keys())
        all_options_to_enable.update(transitive_options_to_enable.keys())
        if all_options_to_enable:
            message = ("Several opencv options which were disabled will be enabled because "
                       "they are required by modules you have explicitly requested:\n")

            for option_to_enable in all_options_to_enable:
                setattr(self.options, option_to_enable, True)

                direct_and_transitive = []
                direct = ", ".join(direct_options_to_enable.get(option_to_enable, []))
                if direct:
                    direct_and_transitive.append(f"direct dependency of {direct}")
                transitive = ", ".join(transitive_options_to_enable.get(option_to_enable, []))
                if transitive:
                    direct_and_transitive.append(f"transitive dependency of {transitive}")
                message += f"  - {option_to_enable}: {' / '.join(direct_and_transitive)}\n"

            self.output.warning(message)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        # TODO: remove contrib option in few months
        if self.options.contrib != "deprecated":
            self.output.warning("contrib option is deprecated")
            if self.options.contrib:
                # During deprecation period, keep old behavior of contrib=True, which was to enable
                # all available contribs.
                ## Filter main module options
                filtered_options = list(OPENCV_MAIN_MODULES_OPTIONS)
                ## Filter extra modules not built previously with contrib=True
                filtered_options.extend(["cvv", "freetype", "hdf", "ovis", "sfm", "viz"])
                ## Filter extra modules not built previously when some option was disabled
                if not self.options.with_eigen:
                    filtered_options.append("alphamat")
                if not self.options.with_cuda:
                    filtered_options.extend([
                        "cudaarithm", "cudabgsegm", "cudacodec", "cudafeatures2d", "cudafilters", "cudaimgproc",
                        "cudalegacy", "cudaobjdetect", "cudaoptflow", "cudastereo", "cudawarping",
                    ])
                for option, values in self._opencv_modules.items():
                    if option not in filtered_options and not values.get("no_option"):
                        try:
                            if hasattr(self.options, option):
                                setattr(self.options, option, True)
                        except ConanException:
                            continue

        # TODO: remove contrib_freetype option in few months
        if self.options.contrib_freetype != "deprecated":
            self.output.warning("contrib_freetype option is deprecated, use freetype option instead")
            self.options.freetype = self.options.contrib_freetype

        # TODO: remove contrib_sfm option in few months
        if self.options.contrib_sfm != "deprecated":
            self.output.warning("contrib_sfm option is deprecated, use sfm option instead")
            self.options.sfm = self.options.contrib_sfm

        # TODO: remove with_ade option in few months
        if self.options.with_ade != "deprecated":
            self.output.warning("with_ade option is deprecated, use gapi option instead")
            self.options.gapi = self.options.with_ade

        # Call this first before any further manipulation of options based on other options
        self._solve_internal_dependency_graph(self._opencv_modules)

        if not self.options.dnn:
            self.options.rm_safe("dnn_cuda")
            self.options.rm_safe("with_vulkan")
        if not self.options.highgui:
            self.options.rm_safe("with_gtk")
        if not (self.options.highgui or self.options.cvv):
            self.options.rm_safe("with_qt")
        if not self.options.imgcodecs:
            self.options.rm_safe("with_jpeg")
            self.options.rm_safe("with_jpeg2000")
            self.options.rm_safe("with_openexr")
            self.options.rm_safe("with_png")
            self.options.rm_safe("with_tiff")
            self.options.rm_safe("with_webp")
            self.options.rm_safe("with_gdal")
            self.options.rm_safe("with_gdcm")
            self.options.rm_safe("with_imgcodec_hdr")
            self.options.rm_safe("with_imgcodec_pfm")
            self.options.rm_safe("with_imgcodec_pxm")
            self.options.rm_safe("with_imgcodec_sunraster")
            self.options.rm_safe("with_msmf")
            self.options.rm_safe("with_msmf_dxva")
        if not self.options.objdetect:
            self.options.rm_safe("with_quirc")
        if not self.options.videoio:
            self.options.rm_safe("with_ffmpeg")
            self.options.rm_safe("with_v4l")
        if not self.options.with_cuda:
            self.options.rm_safe("with_cublas")
            self.options.rm_safe("with_cudnn")
            self.options.rm_safe("with_cufft")
            self.options.rm_safe("dnn_cuda")
            self.options.rm_safe("cuda_arch_bin")
        if not self.options.text:
            self.options.rm_safe("with_tesseract")

        if bool(self.options.get_safe("with_jpeg", False)):
            if self.options.get_safe("with_jpeg2000") == "jasper":
                self.options["jasper"].with_libjpeg = self.options.with_jpeg
            if self.options.get_safe("with_tiff"):
                self.options["libtiff"].jpeg = self.options.with_jpeg

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # core module dependencies
        self.requires("zlib/1.2.13")
        if self.options.with_eigen:
            self.requires("eigen/3.3.9")
        if self.options.parallel == "tbb":
            self.requires("onetbb/2021.7.0")
        if self.options.with_ipp == "intel-ipp":
            self.requires("intel-ipp/2020")
        # dnn module dependencies
        if self.options.dnn:
            self.requires(f"protobuf/{self._protobuf_version}", run=can_run(self))
        if self.options.get_safe("with_vulkan"):
            self.requires("vulkan-headers/1.3.239.0")
        # gapi module dependencies
        if self.options.gapi:
            self.requires("ade/0.1.2a")
        # highgui module dependencies
        if self.options.get_safe("with_gtk"):
            self.requires("gtk/system")
        if self.options.get_safe("with_qt"):
            self.requires("qt/5.15.8")
        # imgcodecs module dependencies
        if self.options.get_safe("with_jpeg") == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.get_safe("with_jpeg") == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.5")
        elif self.options.get_safe("with_jpeg") == "mozjpeg":
            self.requires("mozjpeg/4.1.1")
        if self.options.get_safe("with_jpeg2000") == "jasper":
            self.requires("jasper/4.0.0")
        elif self.options.get_safe("with_jpeg2000") == "openjpeg":
            self.requires("openjpeg/2.5.0")
        if self.options.get_safe("with_png"):
            self.requires("libpng/1.6.39")
        if self.options.get_safe("with_openexr"):
            self.requires("openexr/3.1.5")
        if self.options.get_safe("with_tiff"):
            self.requires("libtiff/4.4.0")
        if self.options.get_safe("with_webp"):
            self.requires("libwebp/1.3.0")
        if self.options.get_safe("with_gdal"):
            self.requires("gdal/3.5.2")
        if self.options.get_safe("with_gdcm"):
            self.requires("gdcm/3.0.20")
        # objdetect module dependencies
        if self.options.get_safe("with_quirc"):
            self.requires("quirc/1.1")
        # videoio module dependencies
        if self.options.get_safe("with_ffmpeg"):
            # opencv doesn't support ffmpeg >= 5.0.0 for the moment (until 4.5.5 at least)
            self.requires("ffmpeg/4.4")
        # freetype module dependencies
        if self.options.freetype:
            self.requires("freetype/2.13.0")
            self.requires("harfbuzz/6.0.0")
        # hdf module dependencies
        if self.options.hdf:
            self.requires("hdf5/1.14.0")
        # ovis module dependencies
        if self.options.ovis:
            self.requires("ogre/1.10.2")
        # sfm module dependencies
        if self.options.sfm:
            self.requires("gflags/2.2.2")
            self.requires("glog/0.6.0")
        # text module dependencies
        if self.options.get_safe("with_tesseract"):
            self.requires("tesseract/5.3.0")

    def package_id(self):
        # deprecated options
        del self.info.options.contrib
        del self.info.options.contrib_freetype
        del self.info.options.contrib_sfm
        del self.info.options.with_ade

    def _check_mandatory_options(self, opencv_modules):
        disabled_options = self._get_mandatory_disabled_options(opencv_modules)
        direct_disabled_mandatory_options = disabled_options["direct"]
        transitive_disabled_mandatory_options = disabled_options["transitive"]

        # check mandatory options
        all_disabled_mandatory_options = set(direct_disabled_mandatory_options.keys())
        all_disabled_mandatory_options.update(transitive_disabled_mandatory_options.keys())
        if all_disabled_mandatory_options:
            message = ("Several opencv options are disabled but are required by modules "
                       "you have explicitly requested:\n")

            for disabled_option in all_disabled_mandatory_options:
                direct_and_transitive = []
                direct = ", ".join(direct_disabled_mandatory_options.get(disabled_option, []))
                if direct:
                    direct_and_transitive.append(f"direct dependency of {direct}")
                transitive = ", ".join(transitive_disabled_mandatory_options.get(disabled_option, []))
                if transitive:
                    direct_and_transitive.append(f"transitive dependency of {transitive}")
                message += f"  - {disabled_option}: {' / '.join(direct_and_transitive)}\n"

            raise ConanInvalidConfiguration(message)

    def validate(self):
        self._check_mandatory_options(self._opencv_modules)
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio with static runtime is not supported for shared library.")
        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "4":
            raise ConanInvalidConfiguration("Clang 3.x can't build OpenCV 4.x due to an internal bug.")
        if self.options.get_safe("dnn_cuda") and \
            (not self.options.with_cuda or not self.options.with_cublas or not self.options.with_cudnn):
            raise ConanInvalidConfiguration("with_cublas and with_cudnn must be enabled for dnn_cuda")
        if self.options.with_ipp == "opencv-icv" and \
           not (self.settings.arch in ["x86", "x86_64"] and self.settings.os in ["Linux", "Macos", "Windows"]):
            raise ConanInvalidConfiguration(f"opencv-icv is not available for {self.settings.os}/{self.settings.arch}")
        if self.options.viz:
            raise ConanInvalidConfiguration(
                "viz module can't be enabled yet. It requires VTK which is not available in conan-center."
            )

    def build_requirements(self):
        if self.options.dnn and not can_run(self):
            self.tool_requires(f"protobuf/{self._protobuf_version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version][0],
            destination=self.source_folder, strip_root=True)

        get(self, **self.conan_data["sources"][self.version][1],
            destination=self._contrib_folder, strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)
        for directory in ["libjasper", "libjpeg-turbo", "libjpeg", "libpng", "libtiff", "libwebp", "openexr", "protobuf", "zlib", "quirc"]:
            rmdir(self, os.path.join(self.source_folder, "3rdparty", directory))

        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "ANDROID OR NOT UNIX", "FALSE")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "elseif(EMSCRIPTEN)", "elseif(QNXNTO)\nelseif(EMSCRIPTEN)")
        replace_in_file(self, os.path.join(self.source_folder, "modules", "imgcodecs", "CMakeLists.txt"), "JASPER_", "Jasper_")
        replace_in_file(self, os.path.join(self.source_folder, "modules", "imgcodecs", "CMakeLists.txt"), "${GDAL_LIBRARY}", "GDAL::GDAL")

        # Fix detection of ffmpeg
        replace_in_file(self, os.path.join(self.source_folder, "modules", "videoio", "cmake", "detect_ffmpeg.cmake"),
                        "FFMPEG_FOUND", "ffmpeg_FOUND")

        # Cleanup RPATH
        if Version(self.version) < "4.1.2":
            install_layout_file = os.path.join(self.source_folder, "CMakeLists.txt")
        else:
            install_layout_file = os.path.join(self.source_folder, "cmake", "OpenCVInstallLayout.cmake")
        replace_in_file(self, install_layout_file,
                              "ocv_update(CMAKE_INSTALL_RPATH \"${CMAKE_INSTALL_PREFIX}/${OPENCV_LIB_INSTALL_PATH}\")",
                              "")
        replace_in_file(self, install_layout_file, "set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)", "")

        if self.options.dnn:
            find_protobuf = os.path.join(self.source_folder, "cmake", "OpenCVFindProtobuf.cmake")
            # OpenCV expects to find FindProtobuf.cmake, not the config file
            replace_in_file(self, find_protobuf,
                            "find_package(Protobuf QUIET)",
                            "find_package(Protobuf REQUIRED MODULE)")
            # in 'if' block, get_target_property() produces an error
            if Version(self.version) >= "4.4.0":
                replace_in_file(self, find_protobuf,
                                      'if(TARGET "${Protobuf_LIBRARIES}")',
                                      'if(FALSE)  # patch: disable if(TARGET "${Protobuf_LIBRARIES}")')

        if self.options.freetype:
            freetype_cmake = os.path.join(self._contrib_folder, "modules", "freetype", "CMakeLists.txt")
            replace_in_file(self, freetype_cmake, "ocv_check_modules(FREETYPE freetype2)", "find_package(Freetype REQUIRED MODULE)")
            replace_in_file(self, freetype_cmake, "FREETYPE_", "Freetype_")

            replace_in_file(self, freetype_cmake, "ocv_check_modules(HARFBUZZ harfbuzz)", "find_package(harfbuzz REQUIRED CONFIG)")
            replace_in_file(self, freetype_cmake, "HARFBUZZ_", "harfbuzz_")

    def generate(self):
        if self.options.dnn:
            if can_run(self):
                VirtualRunEnv(self).generate(scope="build")
            else:
                VirtualBuildEnv(self).generate()

        tc = CMakeToolchain(self)
        tc.variables["OPENCV_CONFIG_INSTALL_PATH"] = "cmake"
        tc.variables["OPENCV_BIN_INSTALL_PATH"] = "bin"
        tc.variables["OPENCV_LIB_INSTALL_PATH"] = "lib"
        tc.variables["OPENCV_3P_LIB_INSTALL_PATH"] = "lib"
        tc.variables["OPENCV_OTHER_INSTALL_PATH"] = "res"
        tc.variables["OPENCV_LICENSES_INSTALL_PATH"] = "licenses"

        tc.variables["OPENCV_SKIP_CMAKE_CXX_STANDARD"] = valid_min_cppstd(self, 11)

        tc.variables["BUILD_CUDA_STUBS"] = False
        tc.variables["BUILD_DOCS"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_FAT_JAVA_LIB"] = False
        tc.variables["BUILD_IPP_IW"] = self.options.with_ipp == "opencv-icv"
        tc.variables["BUILD_ITT"] = False
        tc.variables["BUILD_JASPER"] = False
        tc.variables["BUILD_JAVA"] = False
        tc.variables["BUILD_JPEG"] = False
        tc.variables["BUILD_OPENEXR"] = False
        tc.variables["BUILD_OPENJPEG"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_PROTOBUF"] = False
        tc.variables["BUILD_PACKAGE"] = False
        tc.variables["BUILD_PERF_TESTS"] = False
        tc.variables["BUILD_USE_SYMLINKS"] = False
        tc.variables["BUILD_opencv_apps"] = False
        tc.variables["BUILD_opencv_java"] = False
        tc.variables["BUILD_opencv_java_bindings_gen"] = False
        tc.variables["BUILD_opencv_js"] = False
        tc.variables["BUILD_ZLIB"] = False
        tc.variables["BUILD_PNG"] = False
        tc.variables["BUILD_TIFF"] = False
        tc.variables["BUILD_WEBP"] = False
        tc.variables["BUILD_TBB"] = False
        tc.variables["OPENCV_FORCE_3RDPARTY_BUILD"] = False
        tc.variables["OPENCV_PYTHON_SKIP_DETECTION"] = True
        tc.variables["BUILD_opencv_python2"] = False
        tc.variables["BUILD_opencv_python3"] = False
        tc.variables["BUILD_opencv_python_bindings_g"] = False
        tc.variables["BUILD_opencv_python_tests"] = False
        tc.variables["BUILD_opencv_ts"] = False

        tc.variables["WITH_1394"] = False
        tc.variables["WITH_ARAVIS"] = False
        tc.variables["WITH_CLP"] = False
        tc.variables["WITH_NVCUVID"] = False

        tc.variables["WITH_FFMPEG"] = self.options.get_safe("with_ffmpeg", False)
        if self.options.get_safe("with_ffmpeg"):
            tc.variables["OPENCV_FFMPEG_SKIP_BUILD_CHECK"] = True
            tc.variables["OPENCV_FFMPEG_SKIP_DOWNLOAD"] = True
            # opencv will not search for ffmpeg package, but for
            # libavcodec;libavformat;libavutil;libswscale modules
            tc.variables["OPENCV_FFMPEG_USE_FIND_PACKAGE"] = "ffmpeg"
            tc.variables["OPENCV_INSTALL_FFMPEG_DOWNLOAD_SCRIPT"] = False
            tc.variables["FFMPEG_LIBRARIES"] = "ffmpeg::avcodec;ffmpeg::avdevice;ffmpeg::avformat;ffmpeg::avutil;ffmpeg::swscale"
            for component in ["avcodec", "avdevice", "avformat", "avutil", "swscale"]:
                ffmpeg_component_version = self.dependencies["ffmpeg"].cpp_info.components[component].get_property("component_version")
                tc.variables[f"FFMPEG_lib{component}_VERSION"] = ffmpeg_component_version

        tc.variables["WITH_GSTREAMER"] = False
        tc.variables["WITH_HALIDE"] = False
        tc.variables["WITH_HPX"] = False
        tc.variables["WITH_IMGCODEC_HDR"] = self.options.get_safe("with_imgcodec_hdr", False)
        tc.variables["WITH_IMGCODEC_PFM"] = self.options.get_safe("with_imgcodec_pfm", False)
        tc.variables["WITH_IMGCODEC_PXM"] = self.options.get_safe("with_imgcodec_pxm", False)
        tc.variables["WITH_IMGCODEC_SUNRASTER"] = self.options.get_safe("with_imgcodec_sunraster", False)
        tc.variables["WITH_INF_ENGINE"] = False
        tc.variables["WITH_IPP"] = bool(self.options.with_ipp)
        if self.options.with_ipp == "intel-ipp":
            ipp_root = self.dependencies["intel-ipp"].package_folder.replace("\\", "/")
            tc.variables["IPPROOT"] = ipp_root
            tc.variables["IPPIWROOT"] = ipp_root
        tc.variables["WITH_ITT"] = False
        tc.variables["WITH_LIBREALSENSE"] = False
        tc.variables["WITH_MFX"] = False
        tc.variables["WITH_NGRAPH"] = False
        tc.variables["WITH_OPENCL"] = self.options.get_safe("with_opencl", False)
        tc.variables["WITH_OPENCLAMDBLAS"] = False
        tc.variables["WITH_OPENCLAMDFFT"] = False
        tc.variables["WITH_OPENCL_SVM"] = False
        tc.variables["WITH_OPENGL"] = False
        tc.variables["WITH_TBB"] = self.options.parallel == "tbb"
        tc.variables["WITH_OPENMP"] = self.options.parallel == "openmp"
        tc.variables["WITH_OPENNI"] = False
        tc.variables["WITH_OPENNI2"] = False
        tc.variables["WITH_OPENVX"] = False
        tc.variables["WITH_PLAIDML"] = False
        tc.variables["WITH_PVAPI"] = False
        tc.variables["WITH_QT"] = self.options.get_safe("with_qt", False)
        tc.variables["WITH_QUIRC"] = False
        tc.variables["WITH_V4L"] = self.options.get_safe("with_v4l", False)
        tc.variables["WITH_VA"] = False
        tc.variables["WITH_VA_INTEL"] = False
        tc.variables["WITH_VTK"] = self.options.viz
        tc.variables["WITH_VULKAN"] = self.options.get_safe("with_vulkan", False)
        if self.options.get_safe("with_vulkan"):
            tc.variables["VULKAN_INCLUDE_DIRS"] = os.path.join(self.dependencies["vulkan-headers"].package_folder, "include").replace("\\", "/")
        tc.variables["WITH_XIMEA"] = False
        tc.variables["WITH_XINE"] = False
        tc.variables["WITH_LAPACK"] = False

        tc.variables["WITH_GTK"] = self.options.get_safe("with_gtk", False)
        tc.variables["WITH_GTK_2_X"] = self._is_gtk_version2
        tc.variables["WITH_WEBP"] = self.options.get_safe("with_webp", False)
        tc.variables["WITH_JPEG"] = bool(self.options.get_safe("with_jpeg", False))
        tc.variables["WITH_PNG"] = self.options.get_safe("with_png", False)
        if self._has_with_tiff_option:
            tc.variables["WITH_TIFF"] = self.options.get_safe("with_tiff", False)
        if self._has_with_jpeg2000_option:
            tc.variables["WITH_JASPER"] = self.options.get_safe("with_jpeg2000") == "jasper"
            tc.variables["WITH_OPENJPEG"] = self.options.get_safe("with_jpeg2000") == "openjpeg"
        tc.variables["WITH_OPENEXR"] = self.options.get_safe("with_openexr", False)
        tc.variables["WITH_GDAL"] = self.options.get_safe("with_gdal", False)
        tc.variables["WITH_GDCM"] = self.options.get_safe("with_gdcm", False)
        tc.variables["WITH_EIGEN"] = self.options.with_eigen
        tc.variables["WITH_DSHOW"] = is_msvc(self)
        tc.variables["WITH_MSMF"] = self.options.get_safe("with_msmf", False)
        tc.variables["WITH_MSMF_DXVA"] = self.options.get_safe("with_msmf_dxva", False)
        tc.variables["OPENCV_MODULES_PUBLIC"] = "opencv"
        tc.variables["OPENCV_ENABLE_NONFREE"] = self.options.nonfree

        if self.options.cpu_baseline or self.options.cpu_baseline == "":
            tc.variables["CPU_BASELINE"] = self.options.cpu_baseline

        if self.options.cpu_dispatch or self.options.cpu_dispatch == "":
            tc.variables["CPU_DISPATCH"] = self.options.cpu_dispatch

        tc.variables["ENABLE_NEON"] = self.options.get_safe("neon", False)

        tc.variables["OPENCV_DNN_CUDA"] = self.options.get_safe("dnn_cuda", False)

        # Main modules
        tc.variables["BUILD_opencv_calib3d"] = self.options.calib3d
        tc.variables["BUILD_opencv_core"] = True
        tc.variables["BUILD_opencv_dnn"] = self.options.dnn
        tc.variables["WITH_PROTOBUF"] = self.options.dnn
        if self.options.dnn:
            tc.variables["PROTOBUF_UPDATE_FILES"] = True
        tc.variables["BUILD_opencv_features2d"] = self.options.features2d
        tc.variables["BUILD_opencv_flann"] = self.options.flann
        tc.variables["BUILD_opencv_gapi"] = self.options.gapi
        tc.variables["WITH_ADE"] = self.options.gapi
        tc.variables["BUILD_opencv_highgui"] = self.options.highgui
        tc.variables["BUILD_opencv_imgcodecs"] = self.options.imgcodecs
        tc.variables["BUILD_opencv_imgproc"] = self.options.imgproc
        tc.variables["BUILD_opencv_ml"] = self.options.ml
        tc.variables["BUILD_opencv_objdetect"] = self.options.objdetect
        if self.options.objdetect:
            tc.variables["HAVE_QUIRC"] = self.options.with_quirc  # force usage of quirc requirement
        tc.variables["BUILD_opencv_photo"] = self.options.photo
        tc.variables["BUILD_opencv_stitching"] = self.options.stitching
        tc.variables["BUILD_opencv_video"] = self.options.video
        tc.variables["BUILD_opencv_videoio"] = self.options.videoio
        tc.variables["BUILD_opencv_world"] = self.options.world

        # Extra modules
        tc.variables["OPENCV_EXTRA_MODULES_PATH"] = os.path.join(self._contrib_folder, "modules").replace("\\", "/")
        if self._has_alphamat_option:
            tc.variables["BUILD_opencv_alphamat"] = self.options.alphamat
        tc.variables["BUILD_opencv_aruco"] = self.options.aruco
        if self._has_barcode_option:
            tc.variables["BUILD_opencv_barcode"] = self.options.barcode
        tc.variables["BUILD_opencv_bgsegm"] = self.options.bgsegm
        tc.variables["BUILD_opencv_bioinspired"] = self.options.bioinspired
        tc.variables["BUILD_opencv_ccalib"] = self.options.ccalib
        tc.variables["BUILD_opencv_cnn_3dobj"] = False
        tc.variables["BUILD_opencv_cudaarithm"] = self.options.cudaarithm
        tc.variables["BUILD_opencv_cudabgsegm"] = self.options.cudabgsegm
        tc.variables["BUILD_opencv_cudacodec"] = self.options.cudacodec
        tc.variables["BUILD_opencv_cudafeatures2d"] = self.options.cudafeatures2d
        tc.variables["BUILD_opencv_cudafilters"] = self.options.cudafilters
        tc.variables["BUILD_opencv_cudaimgproc"] = self.options.cudaimgproc
        tc.variables["BUILD_opencv_cudalegacy"] = self.options.cudalegacy
        tc.variables["BUILD_opencv_cudaobjdetect"] = self.options.cudaobjdetect
        tc.variables["BUILD_opencv_cudaoptflow"] = self.options.cudaoptflow
        tc.variables["BUILD_opencv_cudastereo"] = self.options.cudastereo
        tc.variables["BUILD_opencv_cudawarping"] = self.options.cudawarping
        tc.variables["BUILD_opencv_cudev"] = self.options.with_cuda
        tc.variables["BUILD_opencv_cvv"] = self.options.cvv
        tc.variables["BUILD_opencv_datasets"] = self.options.datasets
        tc.variables["BUILD_opencv_dnn_objdetect"] = self.options.dnn_objdetect
        tc.variables["BUILD_opencv_dnn_superres"] = self.options.dnn_superres
        tc.variables["BUILD_opencv_dpm"] = self.options.dpm
        tc.variables["BUILD_opencv_face"] = self.options.face
        tc.variables["BUILD_opencv_freetype"] = self.options.freetype
        tc.variables["BUILD_opencv_fuzzy"] = self.options.fuzzy
        tc.variables["BUILD_opencv_hdf"] = self.options.hdf
        tc.variables["BUILD_opencv_hfs"] = self.options.hfs
        tc.variables["BUILD_opencv_img_hash"] = self.options.img_hash
        if self._has_intensity_transform_option:
            tc.variables["BUILD_opencv_intensity_transform"] = self.options.intensity_transform
        if Version(self.version) >= "4.4.0":
            tc.variables["BUILD_opencv_julia"] = False
        tc.variables["BUILD_opencv_line_descriptor"] = self.options.line_descriptor
        tc.variables["BUILD_opencv_matlab"] = False
        if self._has_mcc_option:
            tc.variables["BUILD_opencv_mcc"] = self.options.mcc
        tc.variables["BUILD_opencv_optflow"] = self.options.optflow
        tc.variables["BUILD_opencv_ovis"] = self.options.ovis
        tc.variables["BUILD_opencv_phase_unwrapping"] = self.options.phase_unwrapping
        tc.variables["BUILD_opencv_plot"] = self.options.plot
        tc.variables["BUILD_opencv_quality"] = self.options.quality
        if self._has_rapid_option:
            tc.variables["BUILD_opencv_rapid"] = self.options.rapid
        tc.variables["BUILD_opencv_reg"] = self.options.reg
        tc.variables["BUILD_opencv_rgbd"] = self.options.rgbd
        tc.variables["BUILD_opencv_saliency"] = self.options.saliency
        tc.variables["BUILD_opencv_sfm"] = self.options.sfm
        tc.variables["BUILD_opencv_shape"] = self.options.shape
        tc.variables["BUILD_opencv_stereo"] = self.options.stereo
        tc.variables["BUILD_opencv_structured_light"] = self.options.structured_light
        tc.variables["BUILD_opencv_superres"] = self.options.get_safe("superres", False)
        tc.variables["BUILD_opencv_surface_matching"] = self.options.surface_matching
        tc.variables["BUILD_opencv_text"] = self.options.text
        if self.options.text:
            tc.variables["WITH_TESSERACT"] = self.options.with_tesseract
        tc.variables["BUILD_opencv_tracking"] = self.options.tracking
        tc.variables["BUILD_opencv_videostab"] = self.options.videostab
        tc.variables["BUILD_opencv_viz"] = self.options.viz
        if self._has_wechat_qrcode_option:
            tc.variables["BUILD_opencv_wechat_qrcode"] = self.options.wechat_qrcode
        tc.variables["BUILD_opencv_xfeatures2d"] = self.options.xfeatures2d
        tc.variables["BUILD_opencv_ximgproc"] = self.options.ximgproc
        tc.variables["BUILD_opencv_xobjdetect"] = self.options.xobjdetect
        tc.variables["BUILD_opencv_xphoto"] = self.options.xphoto

        if self.options.get_safe("with_jpeg2000") == "openjpeg":
            openjpeg_version = Version(self.dependencies["openjpeg"].ref.version)
            tc.variables["OPENJPEG_MAJOR_VERSION"] = openjpeg_version.major
            tc.variables["OPENJPEG_MINOR_VERSION"] = openjpeg_version.minor
            tc.variables["OPENJPEG_BUILD_VERSION"] = openjpeg_version.patch

        tc.variables["WITH_CUDA"] = self.options.with_cuda
        if self.options.with_cuda:
            # This allows compilation on older GCC/NVCC, otherwise build errors.
            tc.variables["CUDA_NVCC_FLAGS"] = "--expt-relaxed-constexpr"
            if self.options.cuda_arch_bin:
                tc.variables["CUDA_ARCH_BIN"] = self.options.cuda_arch_bin
        tc.variables["WITH_CUBLAS"] = self.options.get_safe("with_cublas", False)
        tc.variables["WITH_CUFFT"] = self.options.get_safe("with_cufft", False)
        tc.variables["WITH_CUDNN"] = self.options.get_safe("with_cudnn", False)

        tc.variables["ENABLE_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["ENABLE_CCACHE"] = False

        if is_msvc(self):
            tc.variables["BUILD_WITH_STATIC_CRT"] = is_msvc_static_runtime(self)

        if self.settings.os == "Android":
            tc.variables["BUILD_ANDROID_EXAMPLES"] = False

        tc.generate()

        CMakeDeps(self).generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        if os.path.isfile(os.path.join(self.package_folder, "setup_vars_opencv4.cmd")):
            rename(self, os.path.join(self.package_folder, "setup_vars_opencv4.cmd"),
                         os.path.join(self.package_folder, "res", "setup_vars_opencv4.cmd"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        targets_mapping = {self._cmake_target(k): f"opencv::{self._cmake_target(k)}" for k in self._opencv_modules.keys()}
        if self.options.world:
            targets_mapping.update({"opencv_world": "opencv::opencv_world"})
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            targets_mapping,
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    # returns true if GTK2 is selected. To do this, the version option
    # of the gtk/system package is checked or the conan package version
    # of an gtk conan package is checked.
    @property
    def _is_gtk_version2(self):
        if not self.options.get_safe("with_gtk", False):
            return False
        gtk_version = self.dependencies["gtk"].ref.version
        if gtk_version == "system":
            return self.dependencies["gtk"].options.version == 2
        else:
            return Version(gtk_version) < "3.0.0"

    @staticmethod
    def _cmake_target(module):
        if module in ("ippiw", "correspondence", "multiview", "numeric"):
            return module
        return f"opencv_{module}"

    def package_info(self):
        version = self.version.split(".")
        version = "".join(version) if self.settings.os == "Windows" else ""
        debug = "d" if self.settings.build_type == "Debug" and self.settings.os == "Windows" else ""

        def get_libs(module):
            if module == "ippiw":
                return [
                    f"{module}{debug}",
                    "ippicvmt" if self.settings.os == "Windows" else "ippicv",
                ]
            elif module in ("correspondence", "multiview", "numeric"):
                return [module]
            else:
                libs = [f"opencv_{module}{version}{debug}"]
                if module in ["core", "world"] and not self.options.shared:
                    lib_exclude_filter = "(opencv_|ippi|correspondence|multiview|numeric).*"
                    libs += list(filter(lambda x: not re.match(lib_exclude_filter, x), collect_libs(self)))
                return libs

        def add_components(modules):
            if self.options.world:
                self.cpp_info.components["opencv_world"].set_property("cmake_target_name", "opencv_world")
                self.cpp_info.components["opencv_world"].libs = get_libs("world")
                self.cpp_info.components["opencv_world"].resdirs = ["res"]
                if self.settings.os != "Windows":
                    self.cpp_info.components["opencv_world"].includedirs.append(os.path.join("include", "opencv4"))
                world_requires = set()
                world_requires_exclude = set()
                world_system_libs = set()
                world_frameworks = set()

            for module, values in modules.items():
                if not values.get("is_built"):
                    continue
                cmake_target = self._cmake_target(module)
                conan_component = cmake_target
                # TODO: we should also define COMPONENTS names of each target for find_package() but
                # not possible yet in CMakeDeps. See https://github.com/conan-io/conan/issues/10258
                self.cpp_info.components[conan_component].set_property("cmake_target_name", cmake_target)
                self.cpp_info.components[conan_component].resdirs = ["res"]
                if self.settings.os != "Windows":
                    self.cpp_info.components[conan_component].includedirs.append(os.path.join("include", "opencv4"))

                module_requires = values.get("requires", [])
                module_system_libs = []
                for _condition, _system_libs in values.get("system_libs", []):
                    if _condition:
                        module_system_libs.extend(_system_libs)
                module_frameworks = []
                for _condition, _frameworks in values.get("frameworks", []):
                    if _condition:
                        module_frameworks.extend(_frameworks)

                if self.options.world and values.get("is_part_of_world", True):
                    self.cpp_info.components[conan_component].requires = ["opencv_world"]
                    world_requires.update(module_requires)
                    world_requires_exclude.add(conan_component)
                    world_system_libs.update(module_system_libs)
                    world_frameworks.update(module_frameworks)
                else:
                    self.cpp_info.components[conan_component].libs = get_libs(module)
                    self.cpp_info.components[conan_component].requires = module_requires
                    self.cpp_info.components[conan_component].system_libs = module_system_libs
                    self.cpp_info.components[conan_component].frameworks = module_frameworks

                # TODO: to remove in conan v2 once cmake_find_package* generators removed
                self.cpp_info.components[conan_component].names["cmake_find_package"] = cmake_target
                self.cpp_info.components[conan_component].names["cmake_find_package_multi"] = cmake_target
                self.cpp_info.components[conan_component].build_modules["cmake_find_package"] = [self._module_file_rel_path]
                self.cpp_info.components[conan_component].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
                if module != cmake_target:
                    conan_component_alias = conan_component + "_alias"
                    self.cpp_info.components[conan_component_alias].names["cmake_find_package"] = module
                    self.cpp_info.components[conan_component_alias].names["cmake_find_package_multi"] = module
                    self.cpp_info.components[conan_component_alias].requires = [conan_component]
                    self.cpp_info.components[conan_component_alias].bindirs = []
                    self.cpp_info.components[conan_component_alias].includedirs = []
                    self.cpp_info.components[conan_component_alias].libdirs = []

            if self.options.world:
                self.cpp_info.components["opencv_world"].requires = list(world_requires - world_requires_exclude)
                self.cpp_info.components["opencv_world"].system_libs = list(world_system_libs)
                self.cpp_info.components["opencv_world"].frameworks = list(world_frameworks)

                # TODO: to remove in conan v2 once cmake_find_package* generators removed
                self.cpp_info.components["opencv_world"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
                self.cpp_info.components["opencv_world"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

        self.cpp_info.set_property("cmake_file_name", "OpenCV")

        add_components(self._opencv_modules)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "OpenCV"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCV"
