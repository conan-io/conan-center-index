from conan.tools.microsoft import msvc_runtime_flag
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class OpenCVConan(ConanFile):
    name = "opencv"
    license = "BSD-3-Clause"
    homepage = "https://opencv.org"
    description = "OpenCV (Open Source Computer Vision Library)"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("computer-vision", "deep-learning", "image-processing")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "contrib": [True, False],
        "parallel": [False, "tbb", "openmp"],
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo"],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_jasper": [True, False],
        "with_openexr": [True, False],
        "with_eigen": [True, False],
        "with_webp": [True, False],
        "with_gtk": [True, False],
        "nonfree": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "parallel": False,
        "contrib": False,
        "with_jpeg": "libjpeg",
        "with_png": True,
        "with_tiff": True,
        "with_jasper": True,
        "with_openexr": True,
        "with_eigen": True,
        "with_webp": True,
        "with_gtk": True,
        "nonfree": False,
    }

    short_paths = True
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _contrib_folder(self):
        return "contrib"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_gtk

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        self.options["*"].jpeg = self.options.with_jpeg
        self.options["*"].with_libjpeg = self.options.with_jpeg
        self.options["*"].with_jpeg = self.options.with_jpeg

    def requirements(self):
        self.requires("zlib/1.2.12")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9d")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.2")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_jasper:
            self.requires("jasper/2.0.33")
        if self.options.with_openexr:
            self.requires("openexr/2.5.7")
        if self.options.with_tiff:
            self.requires("libtiff/4.3.0")
        if self.options.with_eigen:
            self.requires("eigen/3.3.9")
        if self.options.parallel == "tbb":
            self.requires("onetbb/2020.3")
        if self.options.with_webp:
            self.requires("libwebp/1.2.2")
        if self.options.contrib:
            self.requires("freetype/2.11.1")
            self.requires("harfbuzz/3.2.0")
            self.requires("gflags/2.2.2")
            self.requires("glog/0.5.0")
        if self.options.get_safe("with_gtk"):
            self.requires("gtk/system")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd") and self.options.with_openexr:
            tools.build.check_min_cppstd(self, self, 11)
        if self.options.shared and self._is_msvc and "MT" in msvc_runtime_flag(self):
            raise ConanInvalidConfiguration("Visual Studio with static runtime is not supported for shared library.")
        if self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) < "4":
            raise ConanInvalidConfiguration("Clang 3.x cannot build OpenCV 3.x due an internal bug.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version][0],
                  destination=self._source_subfolder, strip_root=True)

        tools.files.get(self, **self.conan_data["sources"][self.version][1],
                  destination=self._contrib_folder, strip_root=True)

    def _patch_opencv(self):
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "3rdparty"))
        if self.options.contrib:
            freetype_cmake = os.path.join(self._contrib_folder, "modules", "freetype", "CMakeLists.txt")
            tools.files.replace_in_file(self, freetype_cmake, "ocv_check_modules(FREETYPE freetype2)", "find_package(Freetype REQUIRED)")
            tools.files.replace_in_file(self, freetype_cmake, "FREETYPE_", "Freetype_")

            tools.files.replace_in_file(self, freetype_cmake, "ocv_check_modules(HARFBUZZ harfbuzz)", "find_package(harfbuzz REQUIRED)")
            tools.files.replace_in_file(self, freetype_cmake, "HARFBUZZ_", "harfbuzz_")

        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "CMakeLists.txt"), "ANDROID OR NOT UNIX", "FALSE")
        tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "modules", "imgcodecs", "CMakeLists.txt"), "JASPER_", "Jasper_")

        # Cleanup RPATH
        if tools.Version(self.version) < "3.4.8":
            install_layout_file = os.path.join(self._source_subfolder, "CMakeLists.txt")
        else:
            install_layout_file = os.path.join(self._source_subfolder, "cmake", "OpenCVInstallLayout.cmake")
        tools.files.replace_in_file(self, install_layout_file,
                              "ocv_update(CMAKE_INSTALL_RPATH \"${CMAKE_INSTALL_PREFIX}/${OPENCV_LIB_INSTALL_PATH}\")",
                              "")
        tools.files.replace_in_file(self, install_layout_file, "set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)", "")

        if self.options.contrib and tools.Version(self.version) <= "3.4.12":
            sfm_cmake = os.path.join(self._contrib_folder, "modules", "sfm", "CMakeLists.txt")
            search = '  find_package(Glog QUIET)\nendif()'
            tools.files.replace_in_file(self, sfm_cmake, search, """{}
            if(NOT GFLAGS_LIBRARIES AND TARGET gflags::gflags)
              set(GFLAGS_LIBRARIES gflags::gflags)
            endif()
            if(NOT GLOG_LIBRARIES AND TARGET glog::glog)
              set(GLOG_LIBRARIES glog::glog)
            endif()""".format(search))

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

        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_DOCS"] = False
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_PACKAGE"] = False
        self._cmake.definitions["BUILD_PERF_TESTS"] = False

        self._cmake.definitions["BUILD_JAVA"] = False
        self._cmake.definitions["BUILD_FAT_JAVA_LIB"] = False
        self._cmake.definitions["BUILD_PERF_TESTS"] = False
        self._cmake.definitions["BUILD_ZLIB"] = False
        self._cmake.definitions["BUILD_JPEG"] = False
        self._cmake.definitions["BUILD_PNG"] = False
        self._cmake.definitions["BUILD_TIFF"] = False
        self._cmake.definitions["BUILD_JASPER"] = False
        self._cmake.definitions["BUILD_OPENEXR"] = False
        self._cmake.definitions["BUILD_WEBP"] = False
        self._cmake.definitions["BUILD_TBB"] = False
        self._cmake.definitions["BUILD_JPEG_TURBO_DISABLE"] = True
        self._cmake.definitions["BUILD_IPP_IW"] = False
        self._cmake.definitions["BUILD_ITT"] = False
        self._cmake.definitions["BUILD_PROTOBUF"] = False
        self._cmake.definitions["BUILD_USE_SYMLINKS"] = False
        self._cmake.definitions["OPENCV_FORCE_3RDPARTY_BUILD"] = False
        self._cmake.definitions["BUILD_opencv_java_bindings_gen"] = False
        self._cmake.definitions["BUILD_opencv_js"] = False
        self._cmake.definitions["BUILD_opencv_apps"] = False
        self._cmake.definitions["BUILD_opencv_java"] = False
        self._cmake.definitions["OPENCV_PYTHON_SKIP_DETECTION"] = True
        self._cmake.definitions["BUILD_opencv_python2"] = False
        self._cmake.definitions["BUILD_opencv_python3"] = False
        self._cmake.definitions["BUILD_opencv_python_bindings_g"] = False
        self._cmake.definitions["BUILD_opencv_python_tests"] = False
        self._cmake.definitions["BUILD_opencv_ts"] = False

        self._cmake.definitions["WITH_CUFFT"] = False
        self._cmake.definitions["WITH_CUBLAS"] = False
        self._cmake.definitions["WITH_NVCUVID"] = False
        self._cmake.definitions["WITH_FFMPEG"] = False
        self._cmake.definitions["WITH_GSTREAMER"] = False
        self._cmake.definitions["WITH_OPENCL"] = False
        self._cmake.definitions["WITH_CUDA"] = False
        self._cmake.definitions["WITH_1394"] = False
        self._cmake.definitions["WITH_ADE"] = False
        self._cmake.definitions["WITH_ARAVIS"] = False
        self._cmake.definitions["WITH_CLP"] = False
        self._cmake.definitions["WITH_HALIDE"] = False
        self._cmake.definitions["WITH_HPX"] = False
        self._cmake.definitions["WITH_IMGCODEC_HDR"] = False
        self._cmake.definitions["WITH_IMGCODEC_PFM"] = False
        self._cmake.definitions["WITH_IMGCODEC_PXM"] = False
        self._cmake.definitions["WITH_IMGCODEC_SUNRASTER"] = False
        self._cmake.definitions["WITH_INF_ENGINE"] = False
        self._cmake.definitions["WITH_IPP"] = False
        self._cmake.definitions["WITH_ITT"] = False
        self._cmake.definitions["WITH_LIBREALSENSE"] = False
        self._cmake.definitions["WITH_MFX"] = False
        self._cmake.definitions["WITH_NGRAPH"] = False
        self._cmake.definitions["WITH_OPENCLAMDBLAS"] = False
        self._cmake.definitions["WITH_OPENCLAMDFFT"] = False
        self._cmake.definitions["WITH_OPENCL_SVM"] = False
        self._cmake.definitions["WITH_OPENGL"] = False
        self._cmake.definitions["WITH_OPENNI"] = False
        self._cmake.definitions["WITH_OPENNI2"] = False
        self._cmake.definitions["WITH_OPENVX"] = False
        self._cmake.definitions["WITH_PLAIDML"] = False
        self._cmake.definitions["WITH_PROTOBUF"] = False
        self._cmake.definitions["WITH_PTHREADS_PF"] = False
        self._cmake.definitions["WITH_PVAPI"] = False
        self._cmake.definitions["WITH_QT"] = False
        self._cmake.definitions["WITH_QUIRC"] = False
        self._cmake.definitions["WITH_V4L"] = False
        self._cmake.definitions["WITH_VA"] = False
        self._cmake.definitions["WITH_VA_INTEL"] = False
        self._cmake.definitions["WITH_VTK"] = False
        self._cmake.definitions["WITH_VULKAN"] = False
        self._cmake.definitions["WITH_XIMEA"] = False
        self._cmake.definitions["WITH_XINE"] = False
        self._cmake.definitions["WITH_LAPACK"] = False
        self._cmake.definitions["WITH_IPP_IW"] = False
        self._cmake.definitions["WITH_CAROTENE"] = False
        self._cmake.definitions["WITH_PROTOBUF"] = False
        self._cmake.definitions["WITH_LAPACK"] = False

        self._cmake.definitions["WITH_JPEG"] = self.options.with_jpeg
        self._cmake.definitions["WITH_PNG"] = self.options.with_png
        self._cmake.definitions["WITH_TIFF"] = self.options.with_tiff
        self._cmake.definitions["WITH_JASPER"] = self.options.with_jasper
        self._cmake.definitions["WITH_OPENEXR"] = self.options.with_openexr
        self._cmake.definitions["WITH_EIGEN"] = self.options.with_eigen
        self._cmake.definitions["WITH_WEBP"] = self.options.with_webp
        self._cmake.definitions["WITH_DSHOW"] = self._is_msvc
        self._cmake.definitions["WITH_MSMF"] = self._is_msvc
        self._cmake.definitions["WITH_MSMF_DXVA"] = self._is_msvc
        self._cmake.definitions["WITH_GTK"] = self.options.get_safe("with_gtk", False)
        self._cmake.definitions["WITH_GTK_2_X"] = self.options.get_safe("with_gtk", False)

        self._cmake.definitions["OPENCV_MODULES_PUBLIC"] = "opencv"
        self._cmake.definitions["OPENCV_ENABLE_NONFREE"] = self.options.nonfree
        if self.options.parallel:
            self._cmake.definitions["WITH_TBB"] = self.options.parallel == "tbb"
            self._cmake.definitions["WITH_OPENMP"] = self.options.parallel == "openmp"

        if self.options.contrib:
            self._cmake.definitions["OPENCV_EXTRA_MODULES_PATH"] = os.path.join(self.build_folder, self._contrib_folder, 'modules')

        if self._is_msvc:
            self._cmake.definitions["BUILD_WITH_STATIC_CRT"] = "MT" in msvc_runtime_flag(self)
        if self.options.with_openexr:
            self._cmake.definitions["OPENEXR_ROOT"] = self.deps_cpp_info['openexr'].rootpath.replace("\\", "/")
        self._cmake.definitions["ENABLE_PIC"] = self.options.get_safe("fPIC", True)
        self._cmake.definitions["ENABLE_CCACHE"] = False

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_opencv()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "cmake"))
        if os.path.isfile(os.path.join(self.package_folder, "setup_vars_opencv3.cmd")):
            os.rename(os.path.join(self.package_folder, "setup_vars_opencv3.cmd"),
                      os.path.join(self.package_folder, "res", "setup_vars_opencv3.cmd"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {component["target"]:"opencv::{}".format(component["target"]) for component in self._opencv_components}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.files.save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    @property
    def _opencv_components(self):
        def imageformats_deps():
            components = []
            if self.options.with_jasper:
                components.append("jasper::jasper")
            if self.options.with_png:
                components.append("libpng::libpng")
            if self.options.with_jpeg:
                components.append("{0}::{0}".format(self.options.with_jpeg))
            if self.options.with_tiff:
                components.append("libtiff::libtiff")
            if self.options.with_openexr:
                components.append("openexr::openexr")
            if self.options.with_webp:
                components.append("libwebp::libwebp")
            return components

        def eigen():
            return ["eigen::eigen"] if self.options.with_eigen else []

        def parallel():
            if self.options.parallel:
                return ["onetbb::onetbb"] if self.options.parallel == "tbb" else ["openmp"]
            return []

        def xfeatures2d():
            return ["opencv_xfeatures2d"] if self.options.contrib else []

        def freetype():
            return ["freetype::freetype"] if self.options.contrib else []

        def gtk():
            return ["gtk::gtk"] if self.options.get_safe("with_gtk") else []

        opencv_components = [
            {"target": "opencv_core",       "lib": "core",       "requires": ["zlib::zlib"] + eigen() + parallel()},
            {"target": "opencv_flann",      "lib": "flann",      "requires": ["opencv_core"] + eigen()},
            {"target": "opencv_imgproc",    "lib": "imgproc",    "requires": ["opencv_core"] + eigen()},
            {"target": "opencv_ml",         "lib": "ml",         "requires": ["opencv_core"] + eigen()},
            {"target": "opencv_photo",      "lib": "photo",      "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
            {"target": "opencv_video",      "lib": "video",      "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
            {"target": "opencv_features2d", "lib": "features2d", "requires": ["opencv_core", "opencv_flann", "opencv_imgproc"] + eigen()},
            {"target": "opencv_imgcodecs",  "lib": "imgcodecs",  "requires": ["opencv_core", "opencv_imgproc"] + eigen() + imageformats_deps()},
            {"target": "opencv_shape",      "lib": "shape",      "requires": ["opencv_core", "opencv_imgproc", "opencv_video"] + eigen()},
            {"target": "opencv_videoio",    "lib": "videoio",    "requires": ["opencv_core", "opencv_imgproc", "opencv_imgcodecs"] + eigen()},
            {"target": "opencv_calib3d",    "lib": "calib3d",    "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d"] + eigen()},
            {"target": "opencv_highgui",    "lib": "highgui",    "requires": ["opencv_core", "opencv_imgproc", "opencv_imgcodecs", "opencv_videoio"] + eigen() + gtk() + freetype()},
            {"target": "opencv_objdetect",  "lib": "objdetect",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen()},
            {"target": "opencv_stitching",  "lib": "stitching",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_video", "opencv_features2d", "opencv_shape", "opencv_calib3d"] + xfeatures2d() + eigen()},
            {"target": "opencv_superres",   "lib": "superres",   "requires": ["opencv_core", "opencv_imgproc", "opencv_video", "opencv_imgcodecs", "opencv_videoio"] + eigen()},
            {"target": "opencv_videostab",  "lib": "videostab",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_photo", "opencv_video", "opencv_features2d", "opencv_imgcodecs", "opencv_videoio", "opencv_calib3d"] + eigen()}
        ]
        if self.options.contrib:
            opencv_components.extend([
                {"target": "opencv_phase_unwrapping", "lib": "phase_unwrapping", "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_plot",             "lib": "plot",             "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_reg",              "lib": "reg",              "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_surface_matching", "lib": "surface_matching", "requires": ["opencv_core", "opencv_flann"] + eigen()},
                {"target": "opencv_xphoto",           "lib": "xphoto",           "requires": ["opencv_core", "opencv_imgproc", "opencv_photo"] + eigen()},
                {"target": "opencv_freetype",         "lib": "freetype",         "requires": ["opencv_core", "opencv_imgproc", "freetype::freetype", "harfbuzz::harfbuzz"] + eigen()},
                {"target": "opencv_fuzzy",            "lib": "fuzzy",            "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_hfs",              "lib": "hfs",              "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_img_hash",         "lib": "img_hash",         "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_line_descriptor",  "lib": "line_descriptor",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d"] + eigen()},
                {"target": "opencv_saliency",         "lib": "saliency",         "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d"] + eigen()},
                {"target": "opencv_datasets",         "lib": "datasets",         "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_imgcodecs"] + eigen()},
                {"target": "opencv_rgbd",             "lib": "rgbd",             "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen()},
                {"target": "opencv_stereo",           "lib": "stereo",           "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen()},
                {"target": "opencv_structured_light", "lib": "structured_light", "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_phase_unwrapping", "opencv_features2d", "opencv_calib3d"] + eigen()},
                {"target": "opencv_tracking",         "lib": "tracking",         "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_plot", "opencv_video", "opencv_imgcodecs", "opencv_datasets"] + eigen()},
                {"target": "opencv_xfeatures2d",      "lib": "xfeatures2d",      "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_video", "opencv_features2d", "opencv_shape", "opencv_calib3d"] + eigen()},
                {"target": "opencv_ximgproc",         "lib": "ximgproc",         "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d"] + eigen()},
                {"target": "opencv_xobjdetect",       "lib": "xobjdetect",       "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d", "opencv_objdetect"] + eigen()},
                {"target": "opencv_aruco",            "lib": "aruco",            "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen()},
                {"target": "opencv_bgsegm",           "lib": "bgsegm",           "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_video", "opencv_features2d", "opencv_calib3d"] + eigen()},
                {"target": "opencv_bioinspired",      "lib": "bioinspired",      "requires": ["opencv_core", "opencv_imgproc", "opencv_imgcodecs", "opencv_videoio", "opencv_highgui"] + eigen()},
                {"target": "opencv_ccalib",           "lib": "ccalib",           "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_videoio", "opencv_calib3d", "opencv_highgui"] + eigen()},
                {"target": "opencv_dpm",              "lib": "dpm",              "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_videoio", "opencv_calib3d", "opencv_highgui", "opencv_objdetect"] + eigen()},
                {"target": "opencv_face",             "lib": "face",             "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_photo", "opencv_video", "opencv_features2d", "opencv_calib3d", "opencv_objdetect"] + eigen()},
                {"target": "opencv_optflow",          "lib": "optflow",          "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_video", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d", "opencv_ximgproc"] + eigen()},
                {"target": "opencv_sfm",              "lib": "sfm",              "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_video", "opencv_features2d", "opencv_imgcodecs", "opencv_shape", "opencv_calib3d", "opencv_xfeatures2d", "correspondence", "multiview", "numeric", "glog::glog", "gflags::gflags"] + eigen()},

                {"target": "correspondence",          "lib": "correspondence",   "requires": ["glog::glog", "multiview"] + eigen()},
                {"target": "multiview",               "lib": "multiview",        "requires": ["glog::glog", "numeric"] + eigen()},
                {"target": "numeric",                 "lib": "numeric",          "requires": eigen()},
            ])
        return opencv_components

    def package_info(self):
        version = self.version.split(".")
        version = "".join(version) if self.settings.os == "Windows" else ""
        debug = "d" if self.settings.build_type == "Debug" and self._is_msvc else ""

        def get_lib_name(module):
            if module in ("correspondence", "multiview", "numeric"):
                return module
            else:
                return "opencv_%s%s%s" % (module, version, debug)

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
                self.cpp_info.components[conan_component].libs = [lib_name]
                self.cpp_info.components[conan_component].requires = requires
                if self.settings.os == "Linux":
                    self.cpp_info.components[conan_component].system_libs = ["dl", "m", "pthread", "rt"]

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
                    self.cpp_info.components[conan_component_alias].includedirs = []
                    self.cpp_info.components[conan_component_alias].libdirs = []
                    self.cpp_info.components[conan_component_alias].resdirs = []
                    self.cpp_info.components[conan_component_alias].bindirs = []
                    self.cpp_info.components[conan_component_alias].frameworkdirs = []

        self.cpp_info.set_property("cmake_file_name", "OpenCV")

        add_components(self._opencv_components)

        if self.settings.os == "Windows":
            self.cpp_info.components["opencv_imgcodecs"].system_libs = ["comctl32", "gdi32", "ole32", "setupapi", "ws2_32", "vfw32"]
        elif self.settings.os == "Macos":
            self.cpp_info.components["opencv_imgcodecs"].frameworks = ['OpenCL', 'Accelerate', 'CoreMedia', 'CoreVideo', 'CoreGraphics', 'AVFoundation', 'QuartzCore', 'Cocoa']

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "OpenCV"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCV"
