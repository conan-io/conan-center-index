from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, rename, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
from conans import CMake, tools as tools_legacy
import os
import textwrap

required_conan_version = ">=1.53.0"


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
        "contrib": [True, False],
        "contrib_freetype": [True, False],
        "contrib_sfm": [True, False],
        "parallel": [False, "tbb", "openmp"],
        "with_ipp": [False, "intel-ipp", "opencv-icv"],
        "with_ade": [True, False],
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo"],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_jpeg2000": [False, "jasper", "openjpeg"],
        "with_openexr": [True, False],
        "with_eigen": [True, False],
        "with_webp": [True, False],
        "with_gtk": [True, False],
        "with_quirc": [True, False],
        "with_cuda": [True, False],
        "with_cublas": [True, False],
        "with_cufft": [True, False],
        "with_cudnn": [True, False],
        "with_v4l": [True, False],
        "with_ffmpeg": [True, False],
        "with_imgcodec_hdr": [True, False],
        "with_imgcodec_pfm": [True, False],
        "with_imgcodec_pxm": [True, False],
        "with_imgcodec_sunraster": [True, False],
        "neon": [True, False],
        "dnn": [True, False],
        "dnn_cuda": [True, False],
        "cuda_arch_bin": [None, "ANY"],
        "cpu_baseline": [None, "ANY"],
        "cpu_dispatch": [None, "ANY"],
        "nonfree": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "parallel": False,
        "contrib": False,
        "contrib_freetype": False,
        "contrib_sfm": False,
        "with_ipp": False,
        "with_ade": True,
        "with_jpeg": "libjpeg",
        "with_png": True,
        "with_tiff": True,
        "with_jpeg2000": "jasper",
        "with_openexr": True,
        "with_eigen": True,
        "with_webp": True,
        "with_gtk": True,
        "with_quirc": True,
        "with_cuda": False,
        "with_cublas": False,
        "with_cufft": False,
        "with_cudnn": False,
        "with_v4l": False,
        "with_ffmpeg": True,
        "with_imgcodec_hdr": False,
        "with_imgcodec_pfm": False,
        "with_imgcodec_pxm": False,
        "with_imgcodec_sunraster": False,
        "neon": True,
        "dnn": True,
        "dnn_cuda": False,
        "cuda_arch_bin": None,
        "cpu_baseline": None,
        "cpu_dispatch": None,
        "nonfree": False,
    }

    short_paths = True
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_folder(self):
        return os.path.join(self.source_folder, "src")

    @property
    def _contrib_folder(self):
        return os.path.join(self.source_folder, "contrib")

    @property
    def _build_folder(self):
        return os.path.join(self.source_folder, "build")

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
    def _protobuf_version(self):
        return "3.17.1"

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
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

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.contrib:
            del self.options.contrib_freetype
            del self.options.contrib_sfm
        if not self.options.dnn:
            del self.options.dnn_cuda
        if not self.options.with_cuda:
            del self.options.with_cublas
            del self.options.with_cudnn
            del self.options.with_cufft
            del self.options.dnn_cuda
            del self.options.cuda_arch_bin
        if bool(self.options.with_jpeg):
            if self.options.get_safe("with_jpeg2000") == "jasper":
                self.options["jasper"].with_libjpeg = self.options.with_jpeg
            if self.options.get_safe("with_tiff"):
                self.options["libtiff"].jpeg = self.options.with_jpeg

        if self.settings.os == "Android":
            self.options.with_openexr = False  # disabled because this forces linkage to libc++_shared.so

    def layout(self):
        pass

    def requirements(self):
        self.requires("zlib/1.2.13")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.4")
        if self.options.get_safe("with_jpeg2000") == "jasper":
            self.requires("jasper/3.0.6")
        elif self.options.get_safe("with_jpeg2000") == "openjpeg":
            self.requires("openjpeg/2.5.0")
        if self.options.with_png:
            self.requires("libpng/1.6.39")
        if self.options.with_openexr:
            if Version(self.version) < "4.5.3":
                # opencv < 4.5.3 doesn't support openexr >= 3
                self.requires("openexr/2.5.7")
            else:
                self.requires("openexr/3.1.5")
        if self.options.get_safe("with_tiff"):
            self.requires("libtiff/4.4.0")
        if self.options.with_eigen:
            self.requires("eigen/3.3.9")
        if self.options.get_safe("with_ffmpeg"):
            # opencv doesn't support ffmpeg >= 5.0.0 for the moment (until 4.5.5 at least)
            self.requires("ffmpeg/4.4")
        if self.options.parallel == "tbb":
            self.requires("onetbb/2021.7.0")
        if self.options.with_ipp == "intel-ipp":
            self.requires("intel-ipp/2020")
        if self.options.with_webp:
            self.requires("libwebp/1.2.4")
        if self.options.get_safe("contrib_freetype"):
            self.requires("freetype/2.12.1")
            self.requires("harfbuzz/6.0.0")
        if self.options.get_safe("contrib_sfm"):
            self.requires("gflags/2.2.2")
            self.requires("glog/0.6.0")
        if self.options.with_quirc:
            self.requires("quirc/1.1")
        if self.options.get_safe("with_gtk"):
            self.requires("gtk/system")
        if self.options.dnn:
            self.requires(f"protobuf/{self._protobuf_version}")
        if self.options.with_ade:
            self.requires("ade/0.1.2a")

    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio with static runtime is not supported for shared library.")
        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "4":
            raise ConanInvalidConfiguration("Clang 3.x can't build OpenCV 4.x due to an internal bug.")
        if self.options.with_cuda and not self.options.contrib:
            raise ConanInvalidConfiguration("contrib must be enabled for cuda")
        if self.options.get_safe("dnn_cuda") and \
            (not self.options.with_cuda or not self.options.contrib or not self.options.with_cublas or not self.options.with_cudnn):
            raise ConanInvalidConfiguration("with_cublas, with_cudnn and contrib must be enabled for dnn_cuda")
        if self.options.with_ipp == "opencv-icv" and \
            (not str(self.settings.arch) in ["x86", "x86_64"] or \
             not str(self.settings.os) in ["Linux", "Macos", "Windows"]):
            raise ConanInvalidConfiguration(f"opencv-icv is not available for {self.settings.os}/{self.settings.arch}")

    def build_requirements(self):
        if self.options.dnn and hasattr(self, "settings_build"):
            self.tool_requires(f"protobuf/{self._protobuf_version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version][0],
            destination=self._source_folder, strip_root=True)

        get(self, **self.conan_data["sources"][self.version][1],
            destination=self._contrib_folder, strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)
        for directory in ["libjasper", "libjpeg-turbo", "libjpeg", "libpng", "libtiff", "libwebp", "openexr", "protobuf", "zlib", "quirc"]:
            rmdir(self, os.path.join(self._source_folder, "3rdparty", directory))

        replace_in_file(self, os.path.join(self._source_folder, "CMakeLists.txt"), "ANDROID OR NOT UNIX", "FALSE")
        replace_in_file(self, os.path.join(self._source_folder, "CMakeLists.txt"), "elseif(EMSCRIPTEN)", "elseif(QNXNTO)\nelseif(EMSCRIPTEN)")
        replace_in_file(self, os.path.join(self._source_folder, "modules", "imgcodecs", "CMakeLists.txt"), "JASPER_", "Jasper_")

        # Cleanup RPATH
        if Version(self.version) < "4.1.2":
            install_layout_file = os.path.join(self._source_folder, "CMakeLists.txt")
        else:
            install_layout_file = os.path.join(self._source_folder, "cmake", "OpenCVInstallLayout.cmake")
        replace_in_file(self, install_layout_file,
                              "ocv_update(CMAKE_INSTALL_RPATH \"${CMAKE_INSTALL_PREFIX}/${OPENCV_LIB_INSTALL_PATH}\")",
                              "")
        replace_in_file(self, install_layout_file, "set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)", "")

        if self.options.dnn:
            find_protobuf = os.path.join(self._source_folder, "cmake", "OpenCVFindProtobuf.cmake")
            # variables generated by protobuf recipe have all lowercase prefixes
            replace_in_file(self, find_protobuf,
                                  "find_package(Protobuf QUIET)",
                                  """find_package(Protobuf QUIET)
            if(NOT DEFINED Protobuf_LIBRARIES)
              set(Protobuf_LIBRARIES ${protobuf_LIBRARIES})
            endif()
            if(NOT DEFINED Protobuf_LIBRARY)
              set(Protobuf_LIBRARY ${protobuf_LIBS})
            endif()
            if(NOT DEFINED Protobuf_INCLUDE_DIR)
              set(Protobuf_INCLUDE_DIR ${protobuf_INCLUDE_DIR})
            endif()""")
            # in 'if' block, get_target_property() produces an error
            if Version(self.version) >= "4.4.0":
                replace_in_file(self, find_protobuf,
                                      'if(TARGET "${Protobuf_LIBRARIES}")',
                                      'if(FALSE)  # patch: disable if(TARGET "${Protobuf_LIBRARIES}")')
        if self.options.with_ade:
            ade_cmake = os.path.join(self._source_folder, "modules", "gapi", "cmake", "init.cmake")
            replacement = """find_package(ade REQUIRED)
            if(ade_DIR)"""
            replace_in_file(self, ade_cmake, "if(ade_DIR)", replacement, strict=False)
            replace_in_file(self, ade_cmake, "if (ade_DIR)", replacement, strict=False)
            replace_in_file(self, ade_cmake, "TARGET ade", "TARGET ade::ade")
            gapi_cmake = os.path.join(self._source_folder, "modules", "gapi", "CMakeLists.txt")
            replace_in_file(self, gapi_cmake, " ade)", " ade::ade)")

        if self.options.contrib and self.options.contrib_sfm and Version(self.version) <= "4.5.2":
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

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["OPENCV_CONFIG_INSTALL_PATH"] = "cmake"
        self._cmake.definitions["OPENCV_BIN_INSTALL_PATH"] = "bin"
        self._cmake.definitions["OPENCV_LIB_INSTALL_PATH"] = "lib"
        self._cmake.definitions["OPENCV_3P_LIB_INSTALL_PATH"] = "lib"
        self._cmake.definitions["OPENCV_OTHER_INSTALL_PATH"] = "res"
        self._cmake.definitions["OPENCV_LICENSES_INSTALL_PATH"] = "licenses"

        self._cmake.definitions["BUILD_CUDA_STUBS"] = False
        self._cmake.definitions["BUILD_DOCS"] = False
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_FAT_JAVA_LIB"] = False
        self._cmake.definitions["BUILD_IPP_IW"] = False
        self._cmake.definitions["BUILD_ITT"] = False
        self._cmake.definitions["BUILD_JASPER"] = False
        self._cmake.definitions["BUILD_JAVA"] = False
        self._cmake.definitions["BUILD_JPEG"] = False
        self._cmake.definitions["BUILD_OPENEXR"] = False
        self._cmake.definitions["BUILD_OPENJPEG"] = False
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_PROTOBUF"] = False
        self._cmake.definitions["BUILD_PACKAGE"] = False
        self._cmake.definitions["BUILD_PERF_TESTS"] = False
        self._cmake.definitions["BUILD_USE_SYMLINKS"] = False
        self._cmake.definitions["BUILD_opencv_apps"] = False
        self._cmake.definitions["BUILD_opencv_java"] = False
        self._cmake.definitions["BUILD_opencv_java_bindings_gen"] = False
        self._cmake.definitions["BUILD_opencv_js"] = False
        self._cmake.definitions["BUILD_ZLIB"] = False
        self._cmake.definitions["BUILD_PNG"] = False
        self._cmake.definitions["BUILD_TIFF"] = False
        self._cmake.definitions["BUILD_WEBP"] = False
        self._cmake.definitions["BUILD_TBB"] = False
        self._cmake.definitions["OPENCV_FORCE_3RDPARTY_BUILD"] = False
        self._cmake.definitions["OPENCV_PYTHON_SKIP_DETECTION"] = True
        self._cmake.definitions["BUILD_opencv_python2"] = False
        self._cmake.definitions["BUILD_opencv_python3"] = False
        self._cmake.definitions["BUILD_opencv_python_bindings_g"] = False
        self._cmake.definitions["BUILD_opencv_python_tests"] = False
        self._cmake.definitions["BUILD_opencv_ts"] = False

        self._cmake.definitions["WITH_1394"] = False
        self._cmake.definitions["WITH_ADE"] = False
        self._cmake.definitions["WITH_ARAVIS"] = False
        self._cmake.definitions["WITH_CLP"] = False
        self._cmake.definitions["WITH_NVCUVID"] = False

        self._cmake.definitions["WITH_FFMPEG"] = self.options.get_safe("with_ffmpeg")
        if self.options.get_safe("with_ffmpeg"):
            self._cmake.definitions["OPENCV_FFMPEG_SKIP_BUILD_CHECK"] = True
            self._cmake.definitions["OPENCV_FFMPEG_SKIP_DOWNLOAD"] = True
            # opencv will not search for ffmpeg package, but for
            # libavcodec;libavformat;libavutil;libswscale modules
            self._cmake.definitions["OPENCV_FFMPEG_USE_FIND_PACKAGE"] = "ffmpeg"
            self._cmake.definitions["OPENCV_INSTALL_FFMPEG_DOWNLOAD_SCRIPT"] = False
            self._cmake.definitions["FFMPEG_LIBRARIES"] = "ffmpeg::avcodec;ffmpeg::avformat;ffmpeg::avutil;ffmpeg::swscale"
            for component in ["avcodec", "avformat", "avutil", "swscale", "avresample"]:
                # TODO: use self.dependencies once https://github.com/conan-io/conan/issues/12728 fixed
                ffmpeg_component_version = self.deps_cpp_info["ffmpeg"].components[component].version
                self._cmake.definitions[f"FFMPEG_lib{component}_VERSION"] = ffmpeg_component_version

        self._cmake.definitions["WITH_GSTREAMER"] = False
        self._cmake.definitions["WITH_HALIDE"] = False
        self._cmake.definitions["WITH_HPX"] = False
        self._cmake.definitions["WITH_IMGCODEC_HDR"] = self.options.with_imgcodec_hdr
        self._cmake.definitions["WITH_IMGCODEC_PFM"] = self.options.with_imgcodec_pfm
        self._cmake.definitions["WITH_IMGCODEC_PXM"] = self.options.with_imgcodec_pxm
        self._cmake.definitions["WITH_IMGCODEC_SUNRASTER"] = self.options.with_imgcodec_sunraster
        self._cmake.definitions["WITH_INF_ENGINE"] = False
        self._cmake.definitions["WITH_IPP"] = False
        if self.options.with_ipp:
            self._cmake.definitions["WITH_IPP"] = True
            if self.options.with_ipp == "intel-ipp":
                ipp_root = self.dependencies["intel-ipp"].package_folder.replace("\\", "/")
                if self.settings.os == "Windows":
                    ipp_root = ipp_root.replace("\\", "/")
                self._cmake.definitions["IPPROOT"] = ipp_root
                self._cmake.definitions["IPPIWROOT"] = ipp_root
            else:
                self._cmake.definitions["BUILD_IPP_IW"] = True
        self._cmake.definitions["WITH_ITT"] = False
        self._cmake.definitions["WITH_LIBREALSENSE"] = False
        self._cmake.definitions["WITH_MFX"] = False
        self._cmake.definitions["WITH_NGRAPH"] = False
        self._cmake.definitions["WITH_OPENCL"] = False
        self._cmake.definitions["WITH_OPENCLAMDBLAS"] = False
        self._cmake.definitions["WITH_OPENCLAMDFFT"] = False
        self._cmake.definitions["WITH_OPENCL_SVM"] = False
        self._cmake.definitions["WITH_OPENGL"] = False
        self._cmake.definitions["WITH_OPENMP"] = False
        self._cmake.definitions["WITH_OPENNI"] = False
        self._cmake.definitions["WITH_OPENNI2"] = False
        self._cmake.definitions["WITH_OPENVX"] = False
        self._cmake.definitions["WITH_PLAIDML"] = False
        self._cmake.definitions["WITH_PVAPI"] = False
        self._cmake.definitions["WITH_QT"] = False
        self._cmake.definitions["WITH_QUIRC"] = False
        self._cmake.definitions["WITH_V4L"] = self.options.get_safe("with_v4l", False)
        self._cmake.definitions["WITH_VA"] = False
        self._cmake.definitions["WITH_VA_INTEL"] = False
        self._cmake.definitions["WITH_VTK"] = False
        self._cmake.definitions["WITH_VULKAN"] = False
        self._cmake.definitions["WITH_XIMEA"] = False
        self._cmake.definitions["WITH_XINE"] = False
        self._cmake.definitions["WITH_LAPACK"] = False

        self._cmake.definitions["WITH_GTK"] = self.options.get_safe("with_gtk", False)
        self._cmake.definitions["WITH_GTK_2_X"] = self._is_gtk_version2
        self._cmake.definitions["WITH_WEBP"] = self.options.with_webp
        self._cmake.definitions["WITH_JPEG"] = self.options.with_jpeg != False
        self._cmake.definitions["WITH_PNG"] = self.options.with_png
        if self._has_with_tiff_option:
            self._cmake.definitions["WITH_TIFF"] = self.options.with_tiff
        if self._has_with_jpeg2000_option:
            self._cmake.definitions["WITH_JASPER"] = self.options.with_jpeg2000 == "jasper"
            self._cmake.definitions["WITH_OPENJPEG"] = self.options.with_jpeg2000 == "openjpeg"
        self._cmake.definitions["WITH_OPENEXR"] = self.options.with_openexr
        self._cmake.definitions["WITH_EIGEN"] = self.options.with_eigen
        self._cmake.definitions["HAVE_QUIRC"] = self.options.with_quirc  # force usage of quirc requirement
        self._cmake.definitions["WITH_DSHOW"] = is_msvc(self)
        self._cmake.definitions["WITH_MSMF"] = is_msvc(self)
        self._cmake.definitions["WITH_MSMF_DXVA"] = is_msvc(self)
        self._cmake.definitions["OPENCV_MODULES_PUBLIC"] = "opencv"
        self._cmake.definitions["OPENCV_ENABLE_NONFREE"] = self.options.nonfree

        if self.options.cpu_baseline:
            self._cmake.definitions["CPU_BASELINE"] = self.options.cpu_baseline

        if self.options.cpu_dispatch:
            self._cmake.definitions["CPU_DISPATCH"] = self.options.cpu_dispatch

        if self.options.get_safe("neon") is not None:
            self._cmake.definitions["ENABLE_NEON"] = self.options.get_safe("neon")

        self._cmake.definitions["WITH_PROTOBUF"] = self.options.dnn
        if self.options.dnn:
            self._cmake.definitions["PROTOBUF_UPDATE_FILES"] = True
            self._cmake.definitions["BUILD_opencv_dnn"] = True
        self._cmake.definitions["OPENCV_DNN_CUDA"] = self.options.get_safe("dnn_cuda", False)

        if self.options.contrib:
            self._cmake.definitions["OPENCV_EXTRA_MODULES_PATH"] = os.path.join(self._contrib_folder, "modules")
        self._cmake.definitions["BUILD_opencv_freetype"] = self.options.get_safe("contrib_freetype", False)
        self._cmake.definitions["BUILD_opencv_sfm"] = self.options.get_safe("contrib_sfm", False)

        if self.options.get_safe("with_jpeg2000") == "openjpeg":
            openjpeg_version = Version(self.dependencies["openjpeg"].ref.version)
            self._cmake.definitions["OPENJPEG_MAJOR_VERSION"] = openjpeg_version.major
            self._cmake.definitions["OPENJPEG_MINOR_VERSION"] = openjpeg_version.minor
            self._cmake.definitions["OPENJPEG_BUILD_VERSION"] = openjpeg_version.patch
        if self.options.parallel:
            self._cmake.definitions["WITH_TBB"] = self.options.parallel == "tbb"
            self._cmake.definitions["WITH_OPENMP"] = self.options.parallel == "openmp"

        self._cmake.definitions["WITH_CUDA"] = self.options.with_cuda
        self._cmake.definitions["WITH_ADE"] = self.options.with_ade
        if self.options.with_cuda:
            # This allows compilation on older GCC/NVCC, otherwise build errors.
            self._cmake.definitions["CUDA_NVCC_FLAGS"] = "--expt-relaxed-constexpr"
            if self.options.cuda_arch_bin:
                self._cmake.definitions["CUDA_ARCH_BIN"] = self.options.cuda_arch_bin
        self._cmake.definitions["WITH_CUBLAS"] = self.options.get_safe("with_cublas", False)
        self._cmake.definitions["WITH_CUFFT"] = self.options.get_safe("with_cufft", False)
        self._cmake.definitions["WITH_CUDNN"] = self.options.get_safe("with_cudnn", False)

        self._cmake.definitions["ENABLE_PIC"] = self.options.get_safe("fPIC", True)
        self._cmake.definitions["ENABLE_CCACHE"] = False

        if is_msvc(self):
            self._cmake.definitions["BUILD_WITH_STATIC_CRT"] = is_msvc_static_runtime(self)

        if self.settings.os == "Android":
            self._cmake.definitions["ANDROID_STL"] = "c++_static"
            self._cmake.definitions["ANDROID_NATIVE_API_LEVEL"] = self.settings.os.api_level
            self._cmake.definitions["ANDROID_ABI"] = tools_legacy.to_android_abi(str(self.settings.arch))
            self._cmake.definitions["BUILD_ANDROID_EXAMPLES"] = False
            if "ANDROID_NDK_HOME" in os.environ:
                self._cmake.definitions["ANDROID_NDK"] = os.environ.get("ANDROID_NDK_HOME")

        if cross_building(self):
            # FIXME: too specific and error prone, should be delegated to CMake helper
            cmake_system_processor = {
                "armv8": "aarch64",
                "armv8.3": "aarch64",
            }.get(str(self.settings.arch), str(self.settings.arch))
            self._cmake.definitions["CONAN_OPENCV_SYSTEM_PROCESSOR"] = cmake_system_processor
            # Workaround for cross-build to at least iOS/tvOS/watchOS,
            # when dependencies are found with find_path() and find_library()
            self._cmake.definitions["CMAKE_FIND_ROOT_PATH_MODE_INCLUDE"] = "BOTH"
            self._cmake.definitions["CMAKE_FIND_ROOT_PATH_MODE_LIBRARY"] = "BOTH"

        self._cmake.configure(build_folder=self._build_folder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self._source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = self._configure_cmake()
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
            if self.options.with_png:
                components.append("libpng::libpng")
            if self.options.with_jpeg == "libjpeg":
                components.append("libjpeg::libjpeg")
            elif self.options.with_jpeg == "libjpeg-turbo":
                components.append("libjpeg-turbo::jpeg")
            if self.options.get_safe("with_tiff"):
                components.append("libtiff::libtiff")
            if self.options.with_openexr:
                components.append("openexr::openexr")
            if self.options.with_webp:
                components.append("libwebp::libwebp")
            return components

        def eigen():
            return ["eigen::eigen"] if self.options.with_eigen else []

        def parallel():
            return ["onetbb::onetbb"] if self.options.parallel == "tbb" else []

        def quirc():
            return ["quirc::quirc"] if self.options.with_quirc else []

        def gtk():
            return ["gtk::gtk"] if self.options.get_safe("with_gtk") else []

        def protobuf():
            return ["protobuf::protobuf"] if self.options.dnn else []

        def freetype():
            return ["freetype::freetype"] if self.options.get_safe("contrib_freetype") else []

        def xfeatures2d():
            return ["opencv_xfeatures2d"] if self.options.contrib else []

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

        opencv_components = [
            {"target": "opencv_core",       "lib": "core",       "requires": ["zlib::zlib"] + parallel() + eigen() + ipp()},
            {"target": "opencv_flann",      "lib": "flann",      "requires": ["opencv_core"] + eigen() + ipp()},
            {"target": "opencv_imgproc",    "lib": "imgproc",    "requires": ["opencv_core"] + eigen() + ipp()},
            {"target": "opencv_ml",         "lib": "ml",         "requires": ["opencv_core"] + eigen() + ipp()},
            {"target": "opencv_photo",      "lib": "photo",      "requires": ["opencv_core", "opencv_imgproc"] + eigen() + ipp()},
            {"target": "opencv_features2d", "lib": "features2d", "requires": ["opencv_core", "opencv_flann", "opencv_imgproc"] + eigen() + ipp()},
            {"target": "opencv_imgcodecs",  "lib": "imgcodecs",  "requires": ["opencv_core", "opencv_imgproc", "zlib::zlib"] + eigen() + imageformats_deps() + ipp()},
            {"target": "opencv_videoio",    "lib": "videoio",    "requires": ["opencv_core", "opencv_imgproc", "opencv_imgcodecs"] + eigen() + ffmpeg() + ipp()},
            {"target": "opencv_calib3d",    "lib": "calib3d",    "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d"] + eigen() + ipp()},
            {"target": "opencv_highgui",    "lib": "highgui",    "requires": ["opencv_core", "opencv_imgproc", "opencv_imgcodecs", "opencv_videoio"] + freetype() + eigen() + gtk() + ipp()},
            {"target": "opencv_stitching",  "lib": "stitching",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + xfeatures2d() + eigen() + ipp()},
            {"target": "opencv_video",      "lib": "video",      "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen() + ipp()},
        ]
        if self.options.with_ipp == "opencv-icv" and not self.options.shared:
            opencv_components.extend([
                {"target": "ippiw", "lib": "ippiw", "requires": []}
            ])

        if self.options.dnn:
            opencv_components.extend([
                {"target": "opencv_dnn", "lib": "dnn", "requires": ["opencv_core", "opencv_imgproc"] + protobuf() + ipp()},
                {"target": "opencv_objdetect",  "lib": "objdetect",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen() + quirc() + ipp()},
            ])
        if self.options.contrib:
            opencv_components.extend([
                {"target": "opencv_phase_unwrapping",    "lib": "phase_unwrapping",    "requires": ["opencv_core", "opencv_imgproc"] + eigen() + ipp()},
                {"target": "opencv_plot",                "lib": "plot",                "requires": ["opencv_core", "opencv_imgproc"] + eigen() + ipp()},
                {"target": "opencv_quality",             "lib": "quality",             "requires": ["opencv_core", "opencv_imgproc", "opencv_ml"] + eigen() + ipp()},
                {"target": "opencv_reg",                 "lib": "reg",                 "requires": ["opencv_core", "opencv_imgproc"] + eigen() + ipp()},
                {"target": "opencv_surface_matching",    "lib": "surface_matching",    "requires": ["opencv_core", "opencv_flann"] + eigen() + ipp()},
                {"target": "opencv_xphoto",              "lib": "xphoto",              "requires": ["opencv_core", "opencv_imgproc", "opencv_photo"] + eigen() + ipp()},
                {"target": "opencv_fuzzy",               "lib": "fuzzy",               "requires": ["opencv_core", "opencv_imgproc"] + eigen() + ipp()},
                {"target": "opencv_hfs",                 "lib": "hfs",                 "requires": ["opencv_core", "opencv_imgproc"] + eigen() + ipp()},
                {"target": "opencv_img_hash",            "lib": "img_hash",            "requires": ["opencv_core", "opencv_imgproc"] + eigen() + ipp()},
                {"target": "opencv_line_descriptor",     "lib": "line_descriptor",     "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d"] + eigen() + ipp()},
                {"target": "opencv_saliency",            "lib": "saliency",            "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d"] + eigen() + ipp()},
                {"target": "opencv_datasets",            "lib": "datasets",            "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_imgcodecs"] + eigen() + ipp()},
                {"target": "opencv_rgbd",                "lib": "rgbd",                "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen() + ipp()},
                {"target": "opencv_shape",               "lib": "shape",               "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen() + ipp()},
                {"target": "opencv_structured_light",    "lib": "structured_light",    "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_phase_unwrapping", "opencv_features2d", "opencv_calib3d"] + eigen() + ipp()},
                {"target": "opencv_videostab",           "lib": "videostab",           "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_photo", "opencv_features2d", "opencv_imgcodecs", "opencv_videoio", "opencv_calib3d", "opencv_video"] + eigen() + ipp()},
                {"target": "opencv_xfeatures2d",         "lib": "xfeatures2d",         "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_features2d", "opencv_calib3d", "opencv_shape", ] + eigen() + ipp()},
                {"target": "opencv_ximgproc",            "lib": "ximgproc",            "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d", "opencv_video"] + eigen() + ipp()},
                {"target": "opencv_aruco",               "lib": "aruco",               "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d"] + eigen() + ipp()},
                {"target": "opencv_bgsegm",              "lib": "bgsegm",              "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d", "opencv_video"] + eigen() + ipp()},
                {"target": "opencv_bioinspired",         "lib": "bioinspired",         "requires": ["opencv_core", "opencv_imgproc", "opencv_imgcodecs", "opencv_videoio", "opencv_highgui"] + eigen() + ipp()},
                {"target": "opencv_ccalib",              "lib": "ccalib",              "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_videoio", "opencv_calib3d", "opencv_highgui"] + eigen() + ipp()},
                {"target": "opencv_optflow",             "lib": "optflow",             "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_video", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d", "opencv_video", "opencv_ximgproc"] + eigen() + ipp()},
                {"target": "opencv_superres",            "lib": "superres",            "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_videoio", "opencv_calib3d", "opencv_video", "opencv_ximgproc", "opencv_optflow"] + eigen() + ipp()},
                {"target": "opencv_tracking",            "lib": "tracking",            "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_plot", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d", "opencv_datasets", "opencv_video"] + eigen() + ipp()},
                {"target": "opencv_stereo",              "lib": "stereo",              "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_plot", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d", "opencv_datasets", "opencv_video", "opencv_tracking"] + eigen() + ipp()},
            ])
            if self.options.dnn:
                opencv_components.extend([
                    {"target": "opencv_xobjdetect",          "lib": "xobjdetect",          "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d", "opencv_objdetect"] + eigen() + ipp()},
                    {"target": "opencv_dpm",                 "lib": "dpm",                 "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_videoio", "opencv_calib3d", "opencv_highgui", "opencv_objdetect"] + eigen() + ipp()},
                    {"target": "opencv_face",                "lib": "face",                "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_photo", "opencv_features2d", "opencv_calib3d", "opencv_objdetect"] + eigen() + ipp()}
                ])
            if self.version >= "4.3.0":
                opencv_components.extend([
                    {"target": "opencv_intensity_transform", "lib": "intensity_transform", "requires": ["opencv_core", "opencv_imgproc"] + eigen() + ipp()},
                    {"target": "opencv_alphamat",            "lib": "alphamat",            "requires": ["opencv_core", "opencv_imgproc"] + eigen() + ipp()},
                    {"target": "opencv_rapid",               "lib": "rapid",               "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen() + ipp()},
                ])

            if self.options.get_safe("contrib_freetype"):
                opencv_components.extend([
                    {"target": "opencv_freetype",   "lib": "freetype",          "requires": ["opencv_core", "opencv_imgproc", "freetype::freetype", "harfbuzz::harfbuzz"] + eigen() + ipp()},
                ])

            if self.options.get_safe("contrib_sfm"):
                opencv_components.extend([
                    {"target": "opencv_sfm",        "lib": "sfm",               "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d", "opencv_shape", "opencv_xfeatures2d", "correspondence", "multiview", "numeric", "glog::glog", "gflags::gflags"] + eigen() + ipp()},
                    {"target": "numeric",           "lib": "numeric",           "requires": eigen() + ipp()},
                    {"target": "correspondence",    "lib": "correspondence",    "requires": ["multiview", "glog::glog"] + eigen() + ipp()},
                    {"target": "multiview",         "lib": "multiview",         "requires": ["numeric", "gflags::gflags"] + eigen() + ipp()},
                ])

        if self.options.with_cuda:
            opencv_components.extend([
                {"target": "opencv_cudaarithm",     "lib": "cudaarithm",        "requires": ["opencv_core"] + eigen() + ipp()},
                {"target": "opencv_cudabgsegm",     "lib": "cudabgsegm",        "requires": ["opencv_core", "opencv_video"] + eigen() + ipp()},
                {"target": "opencv_cudacodec",      "lib": "cudacodec",         "requires": ["opencv_core"] + eigen() + ipp()},
                {"target": "opencv_cudafeatures2d", "lib": "cudafeatures2d",    "requires": ["opencv_core", "opencv_cudafilters"] + eigen() + ipp()},
                {"target": "opencv_cudafilters",    "lib": "cudafilters",       "requires": ["opencv_core", "opencv_imgproc"] + eigen() + ipp()},
                {"target": "opencv_cudaimgproc",    "lib": "cudaimgproc",       "requires": ["opencv_core", "opencv_imgproc"] + eigen() + ipp()},
                {"target": "opencv_cudalegacy",     "lib": "cudalegacy",        "requires": ["opencv_core", "opencv_video"] + eigen() + ipp()},
                {"target": "opencv_cudaobjdetect",  "lib": "cudaobjdetect",     "requires": ["opencv_core", "opencv_objdetect"] + eigen() + ipp()},
                {"target": "opencv_cudaoptflow",    "lib": "cudaoptflow",       "requires": ["opencv_core"] + eigen() + ipp()},
                {"target": "opencv_cudastereo",     "lib": "cudastereo",        "requires": ["opencv_core", "opencv_calib3d"] + eigen() + ipp()},
                {"target": "opencv_cudawarping",    "lib": "cudawarping",       "requires": ["opencv_core", "opencv_imgproc"] + eigen() + ipp()},
                {"target": "opencv_cudev",          "lib": "cudev",             "requires": [] + eigen() + ipp()},
            ])

        if self.options.with_ade:
            opencv_components.extend([
                {"target": "opencv_gapi",           "lib": "gapi",              "requires": ["opencv_imgproc", "opencv_calib3d", "opencv_video", "ade::ade"]},
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
                            os.path.join("sdk", "native", "staticlibs", tools_legacy.to_android_abi(str(self.settings.arch))))
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
            self.cpp_info.components["opencv_highgui"].system_libs = ["comctl32", "gdi32", "ole32", "setupapi", "ws2_32", "vfw32"]
        elif self.settings.os == "Macos":
            self.cpp_info.components["opencv_highgui"].frameworks = ["Cocoa"]
            self.cpp_info.components["opencv_videoio"].frameworks = ["Cocoa", "Accelerate", "AVFoundation", "CoreGraphics", "CoreMedia", "CoreVideo", "QuartzCore"]
        elif self.settings.os == "iOS":
            self.cpp_info.components["opencv_videoio"].frameworks = ["AVFoundation", "QuartzCore"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "OpenCV"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCV"
