from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, cross_building, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, rename, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
from conans.tools import to_android_abi
import os
import textwrap

required_conan_version = ">=1.54.0"


class OpenCVConan(ConanFile):
    name = "opencv"
    license = "Apache-2.0"
    homepage = "https://opencv.org"
    description = "OpenCV (Open Source Computer Vision Library)"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("computer-vision", "deep-learning", "image-processing")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        # Main modules
        "calib3d": [True, False],
        "dnn": [True, False],
        "features2d": [True, False],
        "flann": [True, False],
        "gapi": [True, False],
        "highgui": [True, False],
        "imgcodecs": [True, False],
        "imgproc": [True, False],
        "ml": [True, False],
        "objdetect": [True, False],
        "photo": [True, False],
        "stitching": [True, False],
        "video": [True, False],
        "videoio": [True, False],
        # Extra modules
        "contrib_alphamat": [True, False],
        "contrib_aruco": [True, False],
        "contrib_barcode": [True, False],
        "contrib_bgsegm": [True, False],
        "contrib_bioinspired": [True, False],
        "contrib_ccalib": [True, False],
        "contrib_cudaarithm": [True, False],
        "contrib_cudabgsegm": [True, False],
        "contrib_cudacodec": [True, False],
        "contrib_cudafeatures2d": [True, False],
        "contrib_cudafilters": [True, False],
        "contrib_cudaimgproc": [True, False],
        "contrib_cudalegacy": [True, False],
        "contrib_cudaobjdetect": [True, False],
        "contrib_cudaoptflow": [True, False],
        "contrib_cudastereo": [True, False],
        "contrib_cudawarping": [True, False],
        "contrib_cudev": [True, False],
        "contrib_datasets": [True, False],
        "contrib_dnn_objdetect": [True, False],
        "contrib_dnn_superres": [True, False],
        "contrib_dpm": [True, False],
        "contrib_face": [True, False],
        "contrib_freetype": [True, False],
        "contrib_fuzzy": [True, False],
        "contrib_hdf": [True, False],
        "contrib_hfs": [True, False],
        "contrib_img_hash": [True, False],
        "contrib_intensity_transform": [True, False],
        "contrib_line_descriptor": [True, False],
        "contrib_mcc": [True, False],
        "contrib_optflow": [True, False],
        "contrib_ovis": [True, False],
        "contrib_phase_unwrapping": [True, False],
        "contrib_plot": [True, False],
        "contrib_quality": [True, False],
        "contrib_rapid": [True, False],
        "contrib_reg": [True, False],
        "contrib_rgbd": [True, False],
        "contrib_saliency": [True, False],
        "contrib_sfm": [True, False],
        "contrib_shape": [True, False],
        "contrib_stereo": [True, False],
        "contrib_structured_light": [True, False],
        "contrib_superres": [True, False],
        "contrib_surface_matching": [True, False],
        "contrib_text": [True, False],
        "contrib_tracking": [True, False],
        "contrib_videostab": [True, False],
        "contrib_wechat_qrcode": [True, False],
        "contrib_xfeatures2d": [True, False],
        "contrib_ximgproc": [True, False],
        "contrib_xobjdetect": [True, False],
        "contrib_xphoto": [True, False],
        # core options
        "parallel": [False, "tbb", "openmp"],
        "with_ipp": [False, "intel-ipp", "opencv-icv"],
        "with_eigen": [True, False],
        "neon": [True, False],
        "with_cuda": [True, False],
        "with_cublas": [True, False],
        "with_cufft": [True, False],
        "with_cudnn": [True, False],
        "cuda_arch_bin": [None, "ANY"],
        "cpu_baseline": [None, "ANY"],
        "cpu_dispatch": [None, "ANY"],
        "nonfree": [True, False],
        # dnn options
        "dnn_cuda": [True, False],
        # highgui options
        "with_gtk": [True, False],
        # imgcodecs options
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
        # objdetect options
        "with_quirc": [True, False],
        # videoio options
        "with_ffmpeg": [True, False],
        "with_v4l": [True, False],
        # contrib_text options
        "with_tesseract": [True, False],
        # TODO: deprecated options to remove in few months
        "contrib": [True, False, "deprecated"],
        "with_ade": [True, False, "deprecated"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        # Main modules
        "calib3d": True,
        "dnn": True,
        "features2d": True,
        "flann": True,
        "gapi": True,
        "highgui": True,
        "imgcodecs": True,
        "imgproc": True,
        "ml": True,
        "objdetect": True,
        "photo": True,
        "stitching": True,
        "video": True,
        "videoio": True,
        # Extra modules
        "contrib_alphamat": False,
        "contrib_aruco": False,
        "contrib_barcode": False,
        "contrib_bgsegm": False,
        "contrib_bioinspired": False,
        "contrib_ccalib": False,
        "contrib_cudaarithm": False,
        "contrib_cudabgsegm": False,
        "contrib_cudacodec": False,
        "contrib_cudafeatures2d": False,
        "contrib_cudafilters": False,
        "contrib_cudaimgproc": False,
        "contrib_cudalegacy": False,
        "contrib_cudaobjdetect": False,
        "contrib_cudaoptflow": False,
        "contrib_cudastereo": False,
        "contrib_cudawarping": False,
        "contrib_cudev": False,
        "contrib_datasets": False,
        "contrib_dnn_objdetect": False,
        "contrib_dnn_superres": False,
        "contrib_dpm": False,
        "contrib_face": False,
        "contrib_freetype": False,
        "contrib_fuzzy": False,
        "contrib_hdf": False,
        "contrib_hfs": False,
        "contrib_img_hash": False,
        "contrib_intensity_transform": False,
        "contrib_line_descriptor": False,
        "contrib_mcc": False,
        "contrib_optflow": False,
        "contrib_ovis": False,
        "contrib_phase_unwrapping": False,
        "contrib_plot": False,
        "contrib_quality": False,
        "contrib_rapid": False,
        "contrib_reg": False,
        "contrib_rgbd": False,
        "contrib_saliency": False,
        "contrib_sfm": False,
        "contrib_shape": False,
        "contrib_stereo": False,
        "contrib_structured_light": False,
        "contrib_superres": False,
        "contrib_surface_matching": False,
        "contrib_text": False,
        "contrib_tracking": False,
        "contrib_videostab": False,
        "contrib_wechat_qrcode": False,
        "contrib_xfeatures2d": False,
        "contrib_ximgproc": False,
        "contrib_xobjdetect": False,
        "contrib_xphoto": False,
        # core options
        "parallel": False,
        "with_ipp": False,
        "with_eigen": True,
        "neon": True,
        "with_cuda": False,
        "with_cublas": False,
        "with_cufft": False,
        "with_cudnn": False,
        "cuda_arch_bin": None,
        "cpu_baseline": None,
        "cpu_dispatch": None,
        "nonfree": False,
        # dnn options
        "dnn_cuda": False,
        # highgui options
        "with_gtk": True,
        # imgcodecs options
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
        # objdetect options
        "with_quirc": True,
        # videoio options
        "with_ffmpeg": True,
        "with_v4l": False,
        # contrib_text options
        "with_tesseract": True,
        # TODO: deprecated options to remove in few months
        "contrib": "deprecated",
        "with_ade": "deprecated",
    }

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
    def _has_contrib_superres_option(self):
        return self.settings.os != "iOS"

    @property
    def _has_contrib_alphamat_option(self):
        return Version(self.version) >= "4.3.0"

    @property
    def _has_contrib_intensity_transform_option(self):
        return Version(self.version) >= "4.3.0"

    @property
    def _has_contrib_rapid_option(self):
        return Version(self.version) >= "4.3.0"

    @property
    def _has_contrib_mcc_option(self):
        return Version(self.version) >= "4.5.0"

    @property
    def _has_contrib_wechat_qrcode_option(self):
        return Version(self.version) >= "4.5.2"

    @property
    def _has_contrib_barcode_option(self):
        return Version(self.version) >= "4.5.3"

    @property
    def _protobuf_version(self):
        return "3.17.1"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_gtk
            del self.options.with_v4l

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
        if not self._has_contrib_superres_option:
            del self.options.contrib_superres
        if not self._has_contrib_alphamat_option:
            del self.options.contrib_alphamat
        if not self._has_contrib_intensity_transform_option:
            del self.options.contrib_intensity_transform
        if not self._has_contrib_rapid_option:
            del self.options.contrib_rapid
        if not self._has_contrib_mcc_option:
            del self.options.contrib_mcc
        if not self._has_contrib_wechat_qrcode_option:
            del self.options.contrib_wechat_qrcode
        if not self._has_contrib_barcode_option:
            del self.options.contrib_barcode

    @property
    def _modules_mandatory_options(self):
        modules_mandatory_options = {
            "calib3d": ["features2d", "flann", "imgproc"],
            "dnn": ["imgproc"],
            "features2d": ["imgproc"],
            "gapi": ["imgproc"],
            "highgui": ["imgproc"],
            "imgcodecs": ["imgproc"],
            "objdetect": ["calib3d", "imgproc"],
            "photo": ["imgproc"],
            "stitching": ["calib3d", "features2d", "flann", "imgproc"],
            "video": ["imgproc"],
            "videoio": ["imgcodecs", "imgproc"],
            "contrib_alphamat": ["imgproc"],
            "contrib_aruco": ["calib3d", "imgproc"],
            "contrib_barcode": ["dnn", "imgproc"],
            "contrib_bgsegm": ["calib3d", "imgproc", "video"],
            "contrib_ccalib": ["calib3d", "features2d", "highgui", "imgproc"],
            "contrib_cudaarithm": ["with_cuda"],
            "contrib_cudabgsegm": ["with_cuda", "video"],
            "contrib_cudacodec": ["with_cuda", "videoio"],
            "contrib_cudafeatures2d": ["with_cuda", "features2d", "contrib_cudafilters", "contrib_cudawarping"],
            "contrib_cudafilters": ["with_cuda", "imgproc", "contrib_cudaarithm"],
            "contrib_cudaimgproc": ["with_cuda", "imgproc"],
            "contrib_cudalegacy": ["with_cuda", "video"],
            "contrib_cudaobjdetect": ["with_cuda", "objdetect", "contrib_cudaarithm", "contrib_cudawarping"],
            "contrib_cudaoptflow": [
                "with_cuda", "video", "contrib_cudaarithm", "contrib_cudaimgproc",
                "contrib_cudawarping", "contrib_optflow",
            ],
            "contrib_cudastereo": ["with_cuda", "calib3d"],
            "contrib_cudawarping": ["with_cuda", "imgproc"],
            "contrib_cudev": ["with_cuda"],
            "contrib_datasets": ["flann", "imgcodecs", "ml"],
            "contrib_dnn_objdetect": ["dnn", "imgproc"],
            "contrib_dnn_superres": ["dnn", "imgproc"],
            "contrib_dpm": ["imgproc", "objdetect"],
            "contrib_face": ["calib3d", "imgproc", "objdetect", "photo"],
            "contrib_freetype": ["imgproc"],
            "contrib_fuzzy": ["imgproc"],
            "contrib_hfs": ["imgproc"],
            "contrib_img_hash": ["imgproc"],
            "contrib_line_descriptor": ["imgproc"],
            "contrib_mcc": ["calib3d", "dnn", "imgproc"],
            "contrib_optflow": ["calib3d", "flann", "imgcodecs", "imgproc", "video", "contrib_ximgproc"],
            "contrib_ovis": ["calib3d", "imgproc"],
            "contrib_phase_unwrapping": ["imgproc"],
            "contrib_plot": ["imgproc"],
            "contrib_quality": ["imgproc", "ml"],
            "contrib_rapid": ["calib3d", "imgproc"],
            "contrib_reg": ["imgproc"],
            "contrib_rgbd": ["calib3d", "imgproc"],
            "contrib_saliency": ["features2d", "imgproc"],
            "contrib_sfm": ["calib3d", "features2d", "imgcodecs", "contrib_xfeatures2d"],
            "contrib_shape": ["calib3d", "imgproc"],
            "contrib_stereo": ["features2d", "imgproc", "contrib_tracking"],
            "contrib_structured_light": ["calib3d", "imgproc", "contrib_phase_unwrapping"],
            "contrib_superres": ["imgproc", "video", "contrib_optflow"],
            "contrib_surface_matching": ["flann"],
            "contrib_text": ["dnn", "features2d", "imgproc", "ml"],
            "contrib_tracking": ["imgproc", "video"],
            "contrib_videostab": ["calib3d", "features2d", "imgproc", "photo", "video"],
            "contrib_wechat_qrcode": ["dnn", "imgproc"],
            "contrib_xfeatures2d": ["calib3d", "features2d", "imgproc"],
            "contrib_ximgproc": ["calib3d", "imgcodecs", "imgproc", "video"],
            "contrib_xobjdetect": ["imgcodecs", "imgproc", "objdetect"],
            "contrib_xphoto": ["imgproc", "photo"],
        }
        if Version(self.version) < "4.3.0":
            modules_mandatory_options.setdefault("contrib_stereo", []).extend(["calib3d", "video"])
        if Version(self.version) >= "4.4.0":
            modules_mandatory_options.setdefault("contrib_intensity_transform", []).append("imgproc")

        return modules_mandatory_options

    def _solve_internal_dependency_graph(self):
        direct_options_to_enable = {}
        transitive_options_to_enable = {}

        # Check which direct options have to be enabled
        base_options = [option for option in self._modules_mandatory_options.keys() if self.options.get_safe(option)]
        for base_option in base_options:
            for mandatory_option in self._modules_mandatory_options.get(base_option, []):
                if not self.options.get_safe(mandatory_option):
                    direct_options_to_enable.setdefault(mandatory_option, set()).add(base_option)

        # Now traverse the graph to check which transitive options have to be enabled
        def collect_transitive_options(base_option, option):
            for mandatory_option in self._modules_mandatory_options.get(option, []):
                if not self.options.get_safe(mandatory_option):
                    if mandatory_option not in transitive_options_to_enable:
                        transitive_options_to_enable[mandatory_option] = set()
                        collect_transitive_options(base_option, mandatory_option)
                    if base_option not in direct_options_to_enable.get(mandatory_option, set()):
                        transitive_options_to_enable[mandatory_option].add(base_option)

        for base_option in base_options:
            collect_transitive_options(base_option, base_option)

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

        if self.settings.os == "Android":
            self.options.with_openexr = False  # disabled because this forces linkage to libc++_shared.so

        # TODO: remove contrib option in few months
        if self.options.contrib != "deprecated":
            self.output.warning("contrib option is deprecated")
            if self.options.contrib:
                # During deprecation period, keep old behavior of contrib=True, which was to enable
                # all available contribs (except freetype, sfm and new hdf & ovis contribs)
                if self._has_contrib_alphamat_option and self.options.imgproc:
                    self.options.contrib_alphamat = True
                if self.options.calib3d and self.options.imgproc:
                    self.options.contrib_aruco = True
                if self._has_contrib_barcode_option and self.options.dnn and self.options.imgproc:
                    self.options.contrib_barcode = True
                if self.options.calib3d and self.options.imgproc and self.options.video:
                    self.options.contrib_bgsegm = True
                self.options.contrib_bioinspired = True
                if self.options.calib3d and self.options.features2d and self.options.highgui and self.options.imgproc:
                    self.options.contrib_ccalib = True
                if self.options.with_cuda:
                    self.options.contrib_cudaarithm = True
                    if self.options.video:
                        self.options.contrib_cudabgsegm = True
                    if self.options.videoio:
                        self.options.contrib_cudacodec = True
                    if self.options.features2d:
                        self.options.contrib_cudafeatures2d = True
                    if self.options.imgproc:
                        self.options.contrib_cudafilters = True
                        self.options.contrib_cudaimgproc = True
                    if self.options.video:
                        self.options.contrib_cudalegacy = True
                    if self.options.objdetect:
                        self.options.contrib_cudaobjdetect = True
                    if self.options.video:
                        self.options.contrib_cudaoptflow = True
                    if self.options.calib3d:
                        self.options.contrib_cudastereo = True
                    if self.options.imgproc:
                        self.options.contrib_cudawarping = True
                    self.options.contrib_cudev = True
                if self.options.flann and self.options.imgcodecs and self.options.ml:
                    self.options.contrib_datasets = True
                if self.options.dnn and self.options.imgproc:
                    self.options.contrib_dnn_objdetect = True
                    self.options.contrib_dnn_superres = True
                if self.options.imgproc and self.options.objdetect:
                    self.options.contrib_dpm = True
                if self.options.calib3d and self.options.imgproc and self.options.objdetect and self.options.photo:
                    self.options.contrib_face = True
                if self.options.imgproc:
                    self.options.contrib_fuzzy = True
                    self.options.contrib_hfs = True
                    self.options.contrib_img_hash = True
                if self._has_contrib_intensity_transform_option and (Version(self.version) < "4.4.0" or self.options.imgproc):
                    self.options.contrib_intensity_transform = True
                if self.options.imgproc:
                    self.options.contrib_line_descriptor = True
                if self._has_contrib_mcc_option and self.options.calib3d and self.options.dnn and self.options.imgproc:
                    self.options.contrib_mcc = True
                if self.options.calib3d and self.options.flann and self.options.imgcodecs and self.options.imgproc and self.options.video:
                    self.options.contrib_optflow = True
                if self.options.imgproc:
                    self.options.contrib_phase_unwrapping = True
                    self.options.contrib_plot = True
                if self.options.imgproc and self.options.ml:
                    self.options.contrib_quality = True
                if self._has_contrib_rapid_option and self.options.calib3d and self.options.imgproc:
                    self.options.contrib_rapid = True
                if self.options.imgproc:
                    self.options.contrib_reg = True
                if self.options.calib3d and self.options.imgproc:
                    self.options.contrib_rgbd = True
                if self.options.features2d and self.options.imgproc:
                    self.options.contrib_saliency = True
                if self.options.calib3d and self.options.imgproc:
                    self.options.contrib_shape = True
                if self.options.features2d and self.options.imgproc and (Version(self.version) >= "4.3.0" or (self.options.calib3d and self.options.video)):
                    self.options.contrib_stereo = True
                if self.options.calib3d and self.options.imgproc:
                    self.options.contrib_structured_light = True
                if self._has_contrib_superres_option and self.options.imgproc and self.options.video:
                    self.options.contrib_superres = True
                if self.options.flann:
                    self.options.contrib_surface_matching = True
                if self.options.dnn and self.options.features2d and self.options.imgproc and self.options.ml:
                    self.options.contrib_text = True
                if self.options.imgproc:
                    self.options.contrib_tracking = True
                if self.options.calib3d and self.options.features2d and self.options.imgproc and self.options.photo and self.options.video:
                    self.options.contrib_videostab = True
                if self._has_contrib_wechat_qrcode_option and self.options.dnn and self.options.imgproc:
                    self.options.contrib_wechat_qrcode = True
                if self.options.calib3d and self.options.features2d and self.options.imgproc:
                    self.options.contrib_xfeatures2d = True
                if self.options.calib3d and self.options.imgcodecs and self.options.imgproc and self.options.video:
                    self.options.contrib_ximgproc = True
                if self.options.imgcodecs and self.options.imgproc and self.options.objdetect:
                    self.options.contrib_xobjdetect = True
                if self.options.imgproc and self.options.photo:
                    self.options.contrib_xphoto = True

        # TODO: remove with_ade option in few months
        if self.options.with_ade != "deprecated":
            self.output.warning("with_ade option is deprecated, use gapi option instead")
            self.options.gapi = self.options.with_ade

        # Call this first before any further manipulation of options based on other options
        self._solve_internal_dependency_graph()

        if not self.options.dnn:
            self.options.rm_safe("dnn_cuda")
        if not self.options.highgui:
            self.options.rm_safe("with_gtk")
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
        if not self.options.contrib_text:
            self.options.rm_safe("with_tesseract")

        if bool(self.options.get_safe("with_jpeg", False)):
            if self.options.get_safe("with_jpeg2000") == "jasper":
                self.options["jasper"].with_libjpeg = self.options.with_jpeg
            if self.options.get_safe("with_tiff"):
                self.options["libtiff"].jpeg = self.options.with_jpeg

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # core dependencies
        self.requires("zlib/1.2.13")
        if self.options.with_eigen:
            self.requires("eigen/3.3.9")
        if self.options.parallel == "tbb":
            self.requires("onetbb/2021.7.0")
        if self.options.with_ipp == "intel-ipp":
            self.requires("intel-ipp/2020")
        # dnn dependencies
        if self.options.dnn:
            self.requires(f"protobuf/{self._protobuf_version}")
        # gapi dependencies
        if self.options.gapi:
            self.requires("ade/0.1.2a")
        # highgui dependencies
        if self.options.get_safe("with_gtk"):
            self.requires("gtk/system")
        # imgcodecs dependencies
        if self.options.get_safe("with_jpeg") == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.get_safe("with_jpeg") == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.4")
        elif self.options.get_safe("with_jpeg") == "mozjpeg":
            self.requires("mozjpeg/4.1.1")
        if self.options.get_safe("with_jpeg2000") == "jasper":
            self.requires("jasper/4.0.0")
        elif self.options.get_safe("with_jpeg2000") == "openjpeg":
            self.requires("openjpeg/2.5.0")
        if self.options.get_safe("with_png"):
            self.requires("libpng/1.6.39")
        if self.options.get_safe("with_openexr"):
            if Version(self.version) < "4.5.3":
                # opencv < 4.5.3 doesn't support openexr >= 3
                self.requires("openexr/2.5.7")
            else:
                self.requires("openexr/3.1.5")
        if self.options.get_safe("with_tiff"):
            self.requires("libtiff/4.4.0")
        if self.options.get_safe("with_webp"):
            self.requires("libwebp/1.2.4")
        if self.options.get_safe("with_gdal"):
            self.requires("gdal/3.5.2")
        if self.options.get_safe("with_gdcm"):
            self.requires("gdcm/3.0.20")
        # objdetect dependencies
        if self.options.get_safe("with_quirc"):
            self.requires("quirc/1.1")
        # videoio dependencies
        if self.options.get_safe("with_ffmpeg"):
            # opencv doesn't support ffmpeg >= 5.0.0 for the moment (until 4.5.5 at least)
            self.requires("ffmpeg/4.4")
        # contrib_freetype dependencies
        if self.options.contrib_freetype:
            self.requires("freetype/2.12.1")
            self.requires("harfbuzz/6.0.0")
        # contrib_hdf dependencies
        if self.options.contrib_hdf:
            self.requires("hdf5/1.13.1")
        # contrib_ovis dependencies
        if self.options.contrib_ovis:
            self.requires("ogre/1.10.2")
        # contrib_sfm dependencies
        if self.options.contrib_sfm:
            self.requires("gflags/2.2.2")
            self.requires("glog/0.6.0")
        # contrib_text dependencies
        if self.options.get_safe("with_tesseract"):
            self.requires("tesseract/5.2.0")

    def package_id(self):
        # deprecated options
        del self.info.options.contrib
        del self.info.options.with_ade

    def validate(self):
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
            (not str(self.settings.arch) in ["x86", "x86_64"] or \
             not str(self.settings.os) in ["Linux", "Macos", "Windows"]):
            raise ConanInvalidConfiguration(f"opencv-icv is not available for {self.settings.os}/{self.settings.arch}")

    def build_requirements(self):
        if self.options.dnn:
            if hasattr(self, "settings_build") and cross_building(self):
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

        if self.options.contrib_freetype:
            freetype_cmake = os.path.join(self._contrib_folder, "modules", "freetype", "CMakeLists.txt")
            replace_in_file(self, freetype_cmake, "ocv_check_modules(FREETYPE freetype2)", "find_package(Freetype REQUIRED MODULE)")
            replace_in_file(self, freetype_cmake, "FREETYPE_", "Freetype_")

            replace_in_file(self, freetype_cmake, "ocv_check_modules(HARFBUZZ harfbuzz)", "find_package(harfbuzz REQUIRED CONFIG)")
            replace_in_file(self, freetype_cmake, "HARFBUZZ_", "harfbuzz_")

        if self.options.contrib_sfm and Version(self.version) <= "4.5.2":
            sfm_cmake = os.path.join(self._contrib_folder, "modules", "sfm", "CMakeLists.txt")
            ver = Version(self.version)
            if ver <= "4.5.0":
                search = "  find_package(Glog QUIET)\nendif()"
            else:
                search = '  set(GLOG_INCLUDE_DIRS "${GLOG_INCLUDE_DIR}")\nendif()'
            replace_in_file(self, sfm_cmake, search, f"""{search}
            if(NOT GFLAGS_LIBRARIES AND TARGET gflags::gflags)
              set(GFLAGS_LIBRARIES gflags::gflags)
            endif()
            if(NOT GLOG_LIBRARIES AND TARGET glog::glog)
              set(GLOG_LIBRARIES glog::glog)
            endif()""")

    def generate(self):
        if self.options.dnn:
            if hasattr(self, "settings_build") and cross_building(self):
                VirtualBuildEnv(self).generate()
            else:
                VirtualRunEnv(self).generate(scope="build")

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
        tc.variables["BUILD_IPP_IW"] = False
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

        tc.variables["WITH_FFMPEG"] = self.options.get_safe("with_ffmpeg")
        if self.options.get_safe("with_ffmpeg"):
            tc.variables["OPENCV_FFMPEG_SKIP_BUILD_CHECK"] = True
            tc.variables["OPENCV_FFMPEG_SKIP_DOWNLOAD"] = True
            # opencv will not search for ffmpeg package, but for
            # libavcodec;libavformat;libavutil;libswscale modules
            tc.variables["OPENCV_FFMPEG_USE_FIND_PACKAGE"] = "ffmpeg"
            tc.variables["OPENCV_INSTALL_FFMPEG_DOWNLOAD_SCRIPT"] = False
            tc.variables["FFMPEG_LIBRARIES"] = "ffmpeg::avcodec;ffmpeg::avformat;ffmpeg::avutil;ffmpeg::swscale"
            for component in ["avcodec", "avformat", "avutil", "swscale", "avresample"]:
                # TODO: use self.dependencies once https://github.com/conan-io/conan/issues/12728 fixed
                ffmpeg_component_version = self.deps_cpp_info["ffmpeg"].components[component].version
                tc.variables[f"FFMPEG_lib{component}_VERSION"] = ffmpeg_component_version

        tc.variables["WITH_GSTREAMER"] = False
        tc.variables["WITH_HALIDE"] = False
        tc.variables["WITH_HPX"] = False
        tc.variables["WITH_IMGCODEC_HDR"] = self.options.get_safe("with_imgcodec_hdr", False)
        tc.variables["WITH_IMGCODEC_PFM"] = self.options.get_safe("with_imgcodec_pfm", False)
        tc.variables["WITH_IMGCODEC_PXM"] = self.options.get_safe("with_imgcodec_pxm", False)
        tc.variables["WITH_IMGCODEC_SUNRASTER"] = self.options.get_safe("with_imgcodec_sunraster", False)
        tc.variables["WITH_INF_ENGINE"] = False
        tc.variables["WITH_IPP"] = False
        if self.options.with_ipp:
            tc.variables["WITH_IPP"] = True
            if self.options.with_ipp == "intel-ipp":
                ipp_root = self.dependencies["intel-ipp"].package_folder.replace("\\", "/")
                if self.settings.os == "Windows":
                    ipp_root = ipp_root.replace("\\", "/")
                tc.variables["IPPROOT"] = ipp_root
                tc.variables["IPPIWROOT"] = ipp_root
            else:
                tc.variables["BUILD_IPP_IW"] = True
        tc.variables["WITH_ITT"] = False
        tc.variables["WITH_LIBREALSENSE"] = False
        tc.variables["WITH_MFX"] = False
        tc.variables["WITH_NGRAPH"] = False
        tc.variables["WITH_OPENCL"] = False
        tc.variables["WITH_OPENCLAMDBLAS"] = False
        tc.variables["WITH_OPENCLAMDFFT"] = False
        tc.variables["WITH_OPENCL_SVM"] = False
        tc.variables["WITH_OPENGL"] = False
        tc.variables["WITH_OPENMP"] = False
        tc.variables["WITH_OPENNI"] = False
        tc.variables["WITH_OPENNI2"] = False
        tc.variables["WITH_OPENVX"] = False
        tc.variables["WITH_PLAIDML"] = False
        tc.variables["WITH_PVAPI"] = False
        tc.variables["WITH_QT"] = False
        tc.variables["WITH_QUIRC"] = False
        tc.variables["WITH_V4L"] = self.options.get_safe("with_v4l", False)
        tc.variables["WITH_VA"] = False
        tc.variables["WITH_VA_INTEL"] = False
        tc.variables["WITH_VTK"] = False
        tc.variables["WITH_VULKAN"] = False
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
        tc.variables["WITH_MSMF"] = is_msvc(self)
        tc.variables["WITH_MSMF_DXVA"] = is_msvc(self)
        tc.variables["OPENCV_MODULES_PUBLIC"] = "opencv"
        tc.variables["OPENCV_ENABLE_NONFREE"] = self.options.nonfree

        if self.options.cpu_baseline:
            tc.variables["CPU_BASELINE"] = self.options.cpu_baseline

        if self.options.cpu_dispatch:
            tc.variables["CPU_DISPATCH"] = self.options.cpu_dispatch

        if self.options.get_safe("neon") is not None:
            tc.variables["ENABLE_NEON"] = self.options.get_safe("neon")

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

        # Extra modules
        tc.variables["OPENCV_EXTRA_MODULES_PATH"] = os.path.join(self._contrib_folder, "modules").replace("\\", "/")
        if self._has_contrib_alphamat_option:
            tc.variables["BUILD_opencv_alphamat"] = self.options.contrib_alphamat
        tc.variables["BUILD_opencv_aruco"] = self.options.contrib_aruco
        if self._has_contrib_barcode_option:
            tc.variables["BUILD_opencv_barcode"] = self.options.contrib_barcode
        tc.variables["BUILD_opencv_bgsegm"] = self.options.contrib_bgsegm
        tc.variables["BUILD_opencv_bioinspired"] = self.options.contrib_bioinspired
        tc.variables["BUILD_opencv_ccalib"] = self.options.contrib_ccalib
        tc.variables["BUILD_opencv_cnn_3dobj"] = False
        tc.variables["BUILD_opencv_cudaarithm"] = self.options.contrib_cudaarithm
        tc.variables["BUILD_opencv_cudabgsegm"] = self.options.contrib_cudabgsegm
        tc.variables["BUILD_opencv_cudacodec"] = self.options.contrib_cudacodec
        tc.variables["BUILD_opencv_cudafeatures2d"] = self.options.contrib_cudafeatures2d
        tc.variables["BUILD_opencv_cudafilters"] = self.options.contrib_cudafilters
        tc.variables["BUILD_opencv_cudaimgproc"] = self.options.contrib_cudaimgproc
        tc.variables["BUILD_opencv_cudalegacy"] = self.options.contrib_cudalegacy
        tc.variables["BUILD_opencv_cudaobjdetect"] = self.options.contrib_cudaobjdetect
        tc.variables["BUILD_opencv_cudaoptflow"] = self.options.contrib_cudaoptflow
        tc.variables["BUILD_opencv_cudastereo"] = self.options.contrib_cudastereo
        tc.variables["BUILD_opencv_cudawarping"] = self.options.contrib_cudawarping
        tc.variables["BUILD_opencv_cudev"] = self.options.contrib_cudev
        tc.variables["BUILD_opencv_cvv"] = False
        tc.variables["BUILD_opencv_datasets"] = self.options.contrib_datasets
        tc.variables["BUILD_opencv_dnn_objdetect"] = self.options.contrib_dnn_objdetect
        tc.variables["BUILD_opencv_dnn_superres"] = self.options.contrib_dnn_superres
        tc.variables["BUILD_opencv_dpm"] = self.options.contrib_dpm
        tc.variables["BUILD_opencv_face"] = self.options.contrib_face
        tc.variables["BUILD_opencv_freetype"] = self.options.contrib_freetype
        tc.variables["BUILD_opencv_fuzzy"] = self.options.contrib_fuzzy
        tc.variables["BUILD_opencv_hdf"] = self.options.contrib_hdf
        tc.variables["BUILD_opencv_hfs"] = self.options.contrib_hfs
        tc.variables["BUILD_opencv_img_hash"] = self.options.contrib_img_hash
        if self._has_contrib_intensity_transform_option:
            tc.variables["BUILD_opencv_intensity_transform"] = self.options.contrib_intensity_transform
        if Version(self.version) >= "4.4.0":
            tc.variables["BUILD_opencv_julia"] = False
        tc.variables["BUILD_opencv_line_descriptor"] = self.options.contrib_line_descriptor
        tc.variables["BUILD_opencv_matlab"] = False
        if self._has_contrib_mcc_option:
            tc.variables["BUILD_opencv_mcc"] = self.options.contrib_mcc
        tc.variables["BUILD_opencv_optflow"] = self.options.contrib_optflow
        tc.variables["BUILD_opencv_ovis"] = self.options.contrib_ovis
        tc.variables["BUILD_opencv_phase_unwrapping"] = self.options.contrib_phase_unwrapping
        tc.variables["BUILD_opencv_plot"] = self.options.contrib_plot
        tc.variables["BUILD_opencv_quality"] = self.options.contrib_quality
        if self._has_contrib_rapid_option:
            tc.variables["BUILD_opencv_rapid"] = self.options.contrib_rapid
        tc.variables["BUILD_opencv_reg"] = self.options.contrib_reg
        tc.variables["BUILD_opencv_rgbd"] = self.options.contrib_rgbd
        tc.variables["BUILD_opencv_saliency"] = self.options.contrib_saliency
        tc.variables["BUILD_opencv_sfm"] = self.options.contrib_sfm
        tc.variables["BUILD_opencv_shape"] = self.options.contrib_shape
        tc.variables["BUILD_opencv_stereo"] = self.options.contrib_stereo
        tc.variables["BUILD_opencv_structured_light"] = self.options.contrib_structured_light
        tc.variables["BUILD_opencv_superres"] = self.options.get_safe("contrib_superres", False)
        tc.variables["BUILD_opencv_surface_matching"] = self.options.contrib_surface_matching
        tc.variables["BUILD_opencv_text"] = self.options.contrib_text
        if self.options.contrib_text:
            tc.variables["WITH_TESSERACT"] = self.options.with_tesseract
        tc.variables["BUILD_opencv_tracking"] = self.options.contrib_tracking
        tc.variables["BUILD_opencv_videostab"] = self.options.contrib_videostab
        tc.variables["BUILD_opencv_viz"] = False
        if self._has_contrib_wechat_qrcode_option:
            tc.variables["BUILD_opencv_wechat_qrcode"] = self.options.contrib_wechat_qrcode
        tc.variables["BUILD_opencv_xfeatures2d"] = self.options.contrib_xfeatures2d
        tc.variables["BUILD_opencv_ximgproc"] = self.options.contrib_ximgproc
        tc.variables["BUILD_opencv_xobjdetect"] = self.options.contrib_xobjdetect
        tc.variables["BUILD_opencv_xphoto"] = self.options.contrib_xphoto

        if self.options.get_safe("with_jpeg2000") == "openjpeg":
            openjpeg_version = Version(self.dependencies["openjpeg"].ref.version)
            tc.variables["OPENJPEG_MAJOR_VERSION"] = openjpeg_version.major
            tc.variables["OPENJPEG_MINOR_VERSION"] = openjpeg_version.minor
            tc.variables["OPENJPEG_BUILD_VERSION"] = openjpeg_version.patch
        if self.options.parallel:
            tc.variables["WITH_TBB"] = self.options.parallel == "tbb"
            tc.variables["WITH_OPENMP"] = self.options.parallel == "openmp"

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
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {component["target"]:"opencv::{}".format(component["target"]) for component in self._opencv_components}
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
            return self.options["gtk"].version == 2
        else:
            return Version(gtk_version) < "3.0.0"

    @property
    def _opencv_components(self):
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

        def parallel():
            return ["onetbb::onetbb"] if self.options.parallel == "tbb" else []

        def quirc():
            return ["quirc::quirc"] if self.options.get_safe("with_quirc") else []

        def gtk():
            return ["gtk::gtk"] if self.options.get_safe("with_gtk") else []

        def protobuf():
            return ["protobuf::protobuf"] if self.options.dnn else []

        def freetype():
            return ["freetype::freetype"] if self.options.contrib_freetype else []

        def ffmpeg():
            if self.options.get_safe("with_ffmpeg"):
                return [
                        "ffmpeg::avcodec",
                        "ffmpeg::avfilter",
                        "ffmpeg::avformat",
                        "ffmpeg::avutil",
                        "ffmpeg::swresample",
                        "ffmpeg::swscale" ]
            else:
                return [ ]

        def ipp():
            if self.options.with_ipp:
                if self.options.with_ipp == "intel-ipp":
                    return ["intel-ipp::intel-ipp"]
                elif self.options.with_ipp == "opencv-icv" and not self.options.shared:
                    return ["ippiw"]
                else:
                    return []
            else:
                return []

        def opencv_calib3d():
            return ["opencv_calib3d"] if self.options.calib3d else []

        def opencv_cudaarithm():
            return ["opencv_cudaarithm"] if self.options.contrib_cudaarithm else []

        def opencv_cudacodec():
            return ["opencv_cudacodec"] if self.options.contrib_cudacodec else []

        def opencv_cudafeatures2d():
            return ["opencv_cudafeatures2d"] if self.options.contrib_cudafeatures2d else []

        def opencv_cudafilters():
            return ["opencv_cudafilters"] if self.options.contrib_cudafilters else []

        def opencv_cudaimgproc():
            return ["opencv_cudaimgproc"] if self.options.contrib_cudaimgproc else []

        def opencv_cudalegacy():
            return ["opencv_cudalegacy"] if self.options.contrib_cudalegacy else []

        def opencv_cudaoptflow():
            return ["opencv_cudaoptflow"] if self.options.contrib_cudaoptflow else []

        def opencv_cudawarping():
            return ["opencv_cudawarping"] if self.options.contrib_cudawarping else []

        def opencv_dnn():
            return ["opencv_dnn"] if self.options.dnn else []

        def opencv_flann():
            return ["opencv_flann"] if self.options.flann else []

        def opencv_imgcodecs():
            return ["opencv_imgcodecs"] if self.options.imgcodecs else []

        def opencv_video():
            return ["opencv_video"] if self.options.video else []

        def opencv_videoio():
            return ["opencv_videoio"] if self.options.videoio else []

        def opencv_xfeatures2d():
            return ["opencv_xfeatures2d"] if self.options.contrib_xfeatures2d else []

        # Main modules
        opencv_components = [
            {"target": "opencv_core", "lib": "core", "requires": ["zlib::zlib"] + parallel() + eigen() + ipp()},
        ]
        if self.options.with_ipp == "opencv-icv" and not self.options.shared:
            opencv_components.extend([
                {"target": "ippiw", "lib": "ippiw", "requires": []}
            ])
        if self.options.calib3d:
            requires_calib3d = ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_calib3d", "lib": "calib3d", "requires": requires_calib3d},
            ])
        if self.options.dnn:
            requires_dnn = ["opencv_core", "opencv_imgproc"] + protobuf() + ipp()
            opencv_components.extend([
                {"target": "opencv_dnn", "lib": "dnn", "requires": requires_dnn},
            ])
        if self.options.features2d:
            requires_features2d = ["opencv_imgproc"] + opencv_flann() + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_features2d", "lib": "features2d", "requires": requires_features2d},
            ])
        if self.options.flann:
            requires_flann = ["opencv_core"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_flann", "lib": "flann", "requires": requires_flann},
            ])
        if self.options.gapi:
            requires_gapi = ["opencv_imgproc", "ade::ade"]
            if Version(self.version) >= "4.3.0":
                requires_gapi.extend(opencv_video())
            if Version(self.version) >= "4.5.2":
                requires_gapi.extend(opencv_calib3d())
            opencv_components.extend([
                {"target": "opencv_gapi", "lib": "gapi", "requires": requires_gapi},
            ])
        if self.options.highgui:
            requires_highgui = ["opencv_core", "opencv_imgproc"] + opencv_imgcodecs() + \
                               opencv_videoio() + freetype() + gtk() + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_highgui", "lib": "highgui", "requires": requires_highgui},
            ])
        if self.options.imgcodecs:
            requires_imgcodecs = ["opencv_imgproc", "zlib::zlib"] + imageformats_deps() + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_imgcodecs", "lib": "imgcodecs", "requires": requires_imgcodecs},
            ])
        if self.options.imgproc:
            requires_imgproc = ["opencv_core"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_imgproc", "lib": "imgproc", "requires": requires_imgproc},
            ])
        if self.options.ml:
            opencv_components.extend([
                {"target": "opencv_ml", "lib": "ml", "requires": ["opencv_core"] + eigen() + ipp()},
            ])
        if self.options.objdetect:
            requires_objdetect = ["opencv_core", "opencv_imgproc", "opencv_calib3d"] + quirc() + eigen() + ipp()
            if Version(self.version) >= "4.5.4":
                requires_objdetect.extend(opencv_dnn())
            opencv_components.extend([
                {"target": "opencv_objdetect", "lib": "objdetect", "requires": requires_objdetect},
            ])
        if self.options.photo:
            requires_photo = ["opencv_imgproc"] + opencv_cudaarithm() + opencv_cudaimgproc() + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_photo", "lib": "photo", "requires": requires_photo},
            ])
        if self.options.stitching:
            requires_stitching = ["opencv_imgproc", "opencv_features2d", "opencv_calib3d", "opencv_flann"] + \
                                 opencv_xfeatures2d() + opencv_cudaarithm() + opencv_cudawarping() + \
                                 opencv_cudafeatures2d() + opencv_cudalegacy() + opencv_cudaimgproc() + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_stitching", "lib": "stitching", "requires": requires_stitching},
            ])
        if self.options.video:
            requires_video = ["opencv_imgproc"] + opencv_calib3d() + eigen() + ipp()
            if Version(self.version) >= "4.5.1":
                requires_video.extend(opencv_dnn())
            opencv_components.extend([
                {"target": "opencv_video", "lib": "video", "requires": requires_video},
            ])
        if self.options.videoio:
            requires_videoio = ["opencv_imgproc", "opencv_imgcodecs"] + ffmpeg() + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_videoio", "lib": "videoio", "requires": requires_videoio},
            ])

        # Extra modules
        if self.options.get_safe("contrib_alphamat"):
            requires_alphamat = ["opencv_core", "opencv_imgproc"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_alphamat", "lib": "alphamat", "requires": requires_alphamat},
            ])
        if self.options.contrib_aruco:
            requires_aruco = ["opencv_core", "opencv_imgproc", "opencv_calib3d"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_aruco", "lib": "aruco", "requires": requires_aruco},
            ])
        if self.options.get_safe("contrib_barcode"):
            requires_barcode = ["opencv_core", "opencv_imgproc", "opencv_dnn"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_barcode", "lib": "barcode", "requires": requires_barcode},
            ])
        if self.options.contrib_bgsegm:
            requires_bgsegm = ["opencv_core", "opencv_imgproc", "opencv_video", "opencv_calib3d"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_bgsegm", "lib": "bgsegm", "requires": requires_bgsegm},
            ])
        if self.options.contrib_bioinspired:
            requires_bioinspired = ["opencv_core"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_bioinspired", "lib": "bioinspired", "requires": requires_bioinspired},
            ])
        if self.options.contrib_ccalib:
            requires_ccalib = ["opencv_core", "opencv_imgproc", "opencv_calib3d", "opencv_features2d",
                               "opencv_highgui"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_ccalib", "lib": "ccalib", "requires": requires_ccalib},
            ])
        if self.options.contrib_cudaarithm:
            requires_cudaarithm = ["opencv_core"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_cudaarithm", "lib": "cudaarithm", "requires": requires_cudaarithm},
            ])
        if self.options.contrib_cudabgsegm:
            requires_cudabgsegm = ["opencv_video"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_cudabgsegm", "lib": "cudabgsegm", "requires": requires_cudabgsegm},
            ])
        if self.options.contrib_cudacodec:
            requires_cudacodec = ["opencv_core", "opencv_videio"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_cudacodec", "lib": "cudacodec", "requires": requires_cudacodec},
            ])
        if self.options.contrib_cudafeatures2d:
            requires_cudafeatures2d = ["opencv_features2d", "opencv_cudafilters", "opencv_cudawarping"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_cudafeatures2d", "lib": "cudafeatures2d", "requires": requires_cudafeatures2d},
            ])
        if self.options.contrib_cudafilters:
            requires_cudafilters = ["opencv_imgproc", "opencv_cudaarithm"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_cudafilters", "lib": "cudafilters", "requires": requires_cudafilters},
            ])
        if self.options.contrib_cudaimgproc:
            requires_cudaimgproc = ["opencv_imgproc"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_cudaimgproc", "lib": "cudaimgproc", "requires": requires_cudaimgproc},
            ])
        if self.options.contrib_cudalegacy:
            requires_cudalegacy = ["opencv_core", "opencv_video"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_cudalegacy", "lib": "cudalegacy", "requires": requires_cudalegacy},
            ])
        if self.options.contrib_cudaobjdetect:
            requires_cudaobjdetect = ["opencv_objdetect", "opencv_cudaarithm", "opencv_cudawarping"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_cudaobjdetect", "lib": "cudaobjdetect", "requires": requires_cudaobjdetect},
            ])
        if self.options.contrib_cudaoptflow:
            requires_cudaoptflow = ["opencv_video", "opencv_optflow", "opencv_cudaarithm", "opencv_cudawarping",
                                    "contrib_cudaimgproc"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_cudaoptflow", "lib": "cudaoptflow", "requires": requires_cudaoptflow},
            ])
        if self.options.contrib_cudastereo:
            requires_cudastereo = ["opencv_calib3d"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_cudastereo", "lib": "cudastereo", "requires": requires_cudastereo},
            ])
        if self.options.contrib_cudawarping:
            requires_cudawarping = ["opencv_core", "opencv_imgproc"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_cudawarping", "lib": "cudawarping", "requires": requires_cudawarping},
            ])
        if self.options.contrib_cudev:
            requires_cudev = eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_cudev", "lib": "cudev", "requires": requires_cudev},
            ])
        if self.options.contrib_datasets:
            requires_datasets = ["opencv_core", "opencv_imgcodecs", "opencv_ml", "opencv_flann"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_datasets", "lib": "datasets", "requires": requires_datasets},
            ])
        if self.options.contrib_dnn_objdetect:
            requires_dnn_objdetect = ["opencv_core", "opencv_imgproc", "opencv_dnn"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_dnn_objdetect", "lib": "dnn_objdetect", "requires": requires_dnn_objdetect},
            ])
        if self.options.contrib_dnn_superres:
            requires_dnn_superres = ["opencv_core", "opencv_imgproc", "opencv_dnn"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_dnn_superres", "lib": "dnn_superres", "requires": requires_dnn_superres},
            ])
        if self.options.contrib_dpm:
            requires_dpm = ["opencv_core", "opencv_imgproc", "opencv_objdetect"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_dpm", "lib": "dpm", "requires": requires_dpm},
            ])
        if self.options.contrib_face:
            requires_face = ["opencv_core", "opencv_imgproc", "opencv_objdetect", "opencv_calib3d", "opencv_photo"] + \
                            eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_face", "lib": "face", "requires": requires_face},
            ])
        if self.options.contrib_freetype:
            requires_freetype = ["opencv_core", "opencv_imgproc", "freetype::freetype", "harfbuzz::harfbuzz"] + \
                                eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_freetype", "lib": "freetype", "requires": requires_freetype},
            ])
        if self.options.contrib_fuzzy:
            requires_fuzzy = ["opencv_core", "opencv_imgproc"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_fuzzy", "lib": "fuzzy", "requires": requires_fuzzy},
            ])
        if self.options.contrib_hdf:
            requires_hdf = ["opencv_core" + "hdf5::hdf5"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_hdf", "lib": "hdf", "requires": requires_hdf},
            ])
        if self.options.contrib_hfs:
            requires_hfs = ["opencv_core", "opencv_imgproc"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_hfs", "lib": "hfs", "requires": requires_hfs},
            ])
        if self.options.contrib_img_hash:
            requires_img_hash = ["opencv_core", "opencv_imgproc"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_img_hash", "lib": "img_hash", "requires": requires_img_hash},
            ])
        if self.options.get_safe("contrib_intensity_transform"):
            requires_intensity_transform = ["opencv_core"] + eigen() + ipp()
            if Version(self.version) >= "4.4.0":
                requires_intensity_transform.append("opencv_imgproc")
            opencv_components.extend([
                {"target": "opencv_intensity_transform", "lib": "intensity_transform", "requires": requires_intensity_transform},
            ])
        if self.options.contrib_line_descriptor:
            requires_line_descriptor = ["opencv_imgproc"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_line_descriptor", "lib": "line_descriptor", "requires": requires_line_descriptor},
            ])
        if self.options.get_safe("contrib_mcc"):
            requires_mcc = ["opencv_core", "opencv_imgproc", "opencv_calib3d", "opencv_dnn"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_mcc", "lib": "mcc", "requires": requires_mcc},
            ])
        if self.options.contrib_optflow:
            requires_optflow = ["opencv_core", "opencv_imgproc", "opencv_calib3d", "opencv_video", "opencv_ximgproc",
                                "opencv_imgcodecs", "opencv_flann"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_optflow", "lib": "optflow", "requires": requires_optflow},
            ])
        if self.options.contrib_ovis:
            requires_ovis = ["opencv_core", "opencv_imgproc", "opencv_calib3d" + "ogre::ogre"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_ovis", "lib": "ovis", "requires": requires_ovis},
            ])
        if self.options.contrib_phase_unwrapping:
            requires_phase_unwrapping = ["opencv_core", "opencv_imgproc"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_phase_unwrapping", "lib": "phase_unwrapping", "requires": requires_phase_unwrapping},
            ])
        if self.options.contrib_plot:
            requires_plot = ["opencv_core", "opencv_imgproc"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_plot", "lib": "plot", "requires": requires_plot},
            ])
        if self.options.contrib_quality:
            requires_quality = ["opencv_core", "opencv_imgproc", "opencv_ml"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_quality", "lib": "quality", "requires": requires_quality},
            ])
        if self.options.get_safe("contrib_rapid"):
            requires_rapid = ["opencv_core", "opencv_imgproc", "opencv_calib3d"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_rapid", "lib": "rapid", "requires": requires_rapid},
            ])
        if self.options.contrib_reg:
            requires_reg = ["opencv_core", "opencv_imgproc"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_reg", "lib": "reg", "requires": requires_reg},
            ])
        if self.options.contrib_rgbd:
            requires_rgbd = ["opencv_core", "opencv_calib3d", "opencv_imgproc"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_rgbd", "lib": "rgbd", "requires": requires_rgbd},
            ])
        if self.options.contrib_saliency:
            requires_saliency = ["opencv_imgproc", "opencv_features2d"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_saliency", "lib": "saliency", "requires": requires_saliency},
            ])
        if self.options.contrib_sfm:
            requires_sfm = ["opencv_core", "opencv_calib3d", "opencv_features2d", "opencv_xfeatures2d", "opencv_imgcodecs",
                            "correspondence", "multiview", "numeric", "glog::glog", "gflags::gflags"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_sfm",     "lib": "sfm",            "requires": requires_sfm},
                {"target": "numeric",        "lib": "numeric",        "requires": eigen() + ipp()},
                {"target": "correspondence", "lib": "correspondence", "requires": ["multiview", "glog::glog"] + eigen() + ipp()},
                {"target": "multiview",      "lib": "multiview",      "requires": ["numeric", "gflags::gflags"] + eigen() + ipp()},
            ])
        if self.options.contrib_shape:
            requires_shape = ["opencv_core", "opencv_imgproc", "opencv_calib3d"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_shape", "lib": "shape", "requires": requires_shape},
            ])
        if self.options.contrib_stereo:
            requires_stereo = ["opencv_core", "opencv_imgproc", "opencv_features2d", "opencv_tracking"] + eigen() + ipp()
            if Version(self.version) < "4.3.0":
                requires_stereo.extend(["opencv_calib3d", "opencv_video"])
            opencv_components.extend([
                {"target": "opencv_stereo", "lib": "stereo", "requires": requires_stereo},
            ])
        if self.options.contrib_structured_light:
            requires_structured_light = ["opencv_core", "opencv_imgproc", "opencv_calib3d", "opencv_phase_unwrapping"] + \
                                        eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_structured_light", "lib": "structured_light", "requires": requires_structured_light},
            ])
        if self.options.get_safe("contrib_superres"):
            requires_superres = ["opencv_imgproc", "opencv_video", "opencv_optflow"] + opencv_videoio() + \
                                eigen() + ipp() + opencv_cudaarithm() + opencv_cudafilters() + opencv_cudawarping() + \
                                opencv_cudaimgproc() + opencv_cudaoptflow() + opencv_cudacodec()
            opencv_components.extend([
                {"target": "opencv_superres", "lib": "superres", "requires": requires_superres},
            ])
        if self.options.contrib_surface_matching:
            requires_surface_matching = ["opencv_core", "opencv_flann"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_surface_matching", "lib": "surface_matching", "requires": requires_surface_matching},
            ])
        if self.options.contrib_text:
            requires_text = ["opencv_core", "opencv_ml", "opencv_imgproc", "opencv_features2d", "opencv_dnn"] + eigen() + ipp()
            if self.options.with_tesseract:
                requires_text.append("tesseract::tesseract")
            opencv_components.extend([
                {"target": "opencv_text", "lib": "text", "requires": requires_text},
            ])
        if self.options.contrib_tracking:
            requires_tracking = ["opencv_core", "opencv_imgproc", "opencv_video"] + opencv_dnn() + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_tracking", "lib": "tracking", "requires": requires_tracking},
            ])
        if self.options.contrib_videostab:
            requires_videostab = ["opencv_imgproc", "opencv_features2d", "opencv_video", "opencv_photo", "opencv_calib3d"] + \
                                 opencv_videoio() + eigen() + ipp() + opencv_cudawarping() + opencv_cudaoptflow()
            opencv_components.extend([
                {"target": "opencv_videostab", "lib": "videostab", "requires": requires_videostab},
            ])
        if self.options.get_safe("contrib_wechat_qrcode"):
            requires_wechat_qrcode = ["opencv_core", "opencv_imgproc", "opencv_dnn"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_wechat_qrcode", "lib": "wechat_qrcode", "requires": requires_wechat_qrcode},
            ])
        if self.options.contrib_xfeatures2d:
            requires_xfeatures2d = ["opencv_core", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + \
                                   eigen() + ipp() + opencv_cudaarithm()
            opencv_components.extend([
                {"target": "opencv_xfeatures2d", "lib": "xfeatures2d", "requires": requires_xfeatures2d},
            ])
        if self.options.contrib_ximgproc:
            requires_ximgproc = ["opencv_core", "opencv_imgproc", "opencv_calib3d", "opencv_imgcodecs", "opencv_video"] + \
                                eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_ximgproc", "lib": "ximgproc", "requires": requires_ximgproc},
            ])
        if self.options.contrib_xobjdetect:
            requires_xobjdetect = ["opencv_core", "opencv_imgproc", "opencv_objdetect", "opencv_imgcodecs"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_xobjdetect", "lib": "xobjdetect", "requires": requires_xobjdetect},
            ])
        if self.options.contrib_xphoto:
            requires_xphoto = ["opencv_core", "opencv_imgproc", "opencv_photo"] + eigen() + ipp()
            opencv_components.extend([
                {"target": "opencv_xphoto", "lib": "xphoto", "requires": requires_xphoto},
            ])

        return opencv_components

    def package_info(self):
        version = self.version.split(".")
        version = "".join(version) if self.settings.os == "Windows" else ""
        debug = "d" if self.settings.build_type == "Debug" and self.settings.os == "Windows" else ""

        def get_lib_name(module):
            if module == "ippiw":
                return f"{module}{debug}"
            elif module in ("correspondence", "multiview", "numeric"):
                return module
            else:
                return f"opencv_{module}{version}{debug}"

        def add_components(components):
            for component in components:
                conan_component = component["target"]
                cmake_target = component["target"]
                cmake_component = component["lib"]
                lib_name = get_lib_name(component["lib"])
                requires = component["requires"]
                # TODO: we should also define COMPONENTS names of each target for find_package() but not possible yet in CMakeDeps
                #       see https://github.com/conan-io/conan/issues/10258
                self.cpp_info.components[conan_component].set_property("cmake_target_name", cmake_target)
                self.cpp_info.components[conan_component].libs = [lib_name]
                if lib_name.startswith("ippiw"):
                    self.cpp_info.components[conan_component].libs.append("ippicvmt" if self.settings.os == "Windows" else "ippicv")
                if self.settings.os != "Windows":
                    self.cpp_info.components[conan_component].includedirs.append(os.path.join("include", "opencv4"))
                self.cpp_info.components[conan_component].requires = requires
                if self.settings.os == "Linux":
                    self.cpp_info.components[conan_component].system_libs = ["dl", "m", "pthread", "rt"]

                if self.settings.os == "Android":
                    self.cpp_info.components[conan_component].includedirs = [
                        os.path.join("sdk", "native", "jni", "include")]
                    self.cpp_info.components[conan_component].system_libs.append("log")
                    if int(str(self.settings.os.api_level)) > 20:
                        self.cpp_info.components[conan_component].system_libs.append("mediandk")
                    if not self.options.shared:
                        self.cpp_info.components[conan_component].libdirs.append(
                            os.path.join("sdk", "native", "staticlibs", to_android_abi(str(self.settings.arch))))
                        if conan_component == "opencv_core":
                            self.cpp_info.components[conan_component].libdirs.append("lib")
                            self.cpp_info.components[conan_component].libs += collect_libs(self)

                if self.settings.os in ["iOS", "Macos", "Linux", "Neutrino"]:
                    if not self.options.shared:
                        if conan_component == "opencv_core":
                            libs = list(filter(lambda x: not x.startswith("opencv"), collect_libs(self)))
                            self.cpp_info.components[conan_component].libs += libs

                # TODO: to remove in conan v2 once cmake_find_package* generators removed
                self.cpp_info.components[conan_component].names["cmake_find_package"] = cmake_target
                self.cpp_info.components[conan_component].names["cmake_find_package_multi"] = cmake_target
                self.cpp_info.components[conan_component].build_modules["cmake_find_package"] = [self._module_file_rel_path]
                self.cpp_info.components[conan_component].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
                if cmake_component != cmake_target:
                    conan_component_alias = conan_component + "_alias"
                    self.cpp_info.components[conan_component_alias].names["cmake_find_package"] = cmake_component
                    self.cpp_info.components[conan_component_alias].names["cmake_find_package_multi"] = cmake_component
                    self.cpp_info.components[conan_component_alias].requires = [conan_component]
                    self.cpp_info.components[conan_component_alias].bindirs = []
                    self.cpp_info.components[conan_component_alias].includedirs = []
                    self.cpp_info.components[conan_component_alias].libdirs = []

        self.cpp_info.set_property("cmake_file_name", "OpenCV")

        add_components(self._opencv_components)

        if self.settings.os == "Windows":
            if self.options.gapi:
                self.cpp_info.components["opencv_gapi"].system_libs = ["ws2_32", "wsock32"]
            if self.options.highgui:
                self.cpp_info.components["opencv_highgui"].system_libs = ["comctl32", "gdi32", "ole32", "setupapi", "ws2_32", "vfw32"]
        elif self.settings.os == "Macos":
            if self.options.imgcodecs:
                self.cpp_info.components["opencv_imgcodecs"].frameworks = ["AppKit", "CoreFoundation", "CoreGraphics"]
            if self.options.highgui:
                self.cpp_info.components["opencv_highgui"].frameworks = ["Cocoa"]
            if self.options.videoio:
                self.cpp_info.components["opencv_videoio"].frameworks = ["Cocoa", "Accelerate", "AVFoundation", "CoreGraphics", "CoreMedia", "CoreVideo", "QuartzCore"]
        elif self.settings.os == "iOS":
            if self.options.imgcodecs:
                self.cpp_info.components["opencv_imgcodecs"].frameworks = ["UIKit", "CoreFoundation", "CoreGraphics"]
            if self.options.videoio:
                self.cpp_info.components["opencv_videoio"].frameworks = ["AVFoundation", "QuartzCore"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "OpenCV"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCV"
