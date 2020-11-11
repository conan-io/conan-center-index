from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.29.1"


class OpenCVConan(ConanFile):
    name = "opencv"
    license = "BSD-3-Clause"
    homepage = "https://opencv.org"
    description = "OpenCV (Open Source Computer Vision Library)"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("computer-vision", "deep-learning", "image-processing")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "contrib": [True, False],
               "with_jpeg": [True, False],
               "with_png": [True, False],
               "with_tiff": [True, False],
               "with_jasper": [True, False],
               "with_openexr": [True, False],
               "with_eigen": [True, False],
               "with_webp": [True, False],
               "with_tbb": [True, False],
               "with_gtk": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "contrib": False,
                       "with_jpeg": True,
                       "with_png": True,
                       "with_tiff": True,
                       "with_jasper": True,
                       "with_openexr": True,
                       "with_eigen": True,
                       "with_webp": True,
                       "with_tbb": False,
                       "with_gtk": True}
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.gtk

    def configure(self):
        if self.settings.compiler == "Visual Studio" and \
           "MT" in str(self.settings.compiler.runtime) and self.options.shared:
            raise ConanInvalidConfiguration("Visual Studio and Runtime MT is not supported for shared library.")
        if self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) < "4":
            raise ConanInvalidConfiguration("Clang 3.x can build OpenCV 3.x due an internal bug.")
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.with_jpeg:
            self.requires("libjpeg/9d")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_jasper:
            self.requires("jasper/2.0.16")
        if self.options.with_openexr:
            self.requires("openexr/2.5.2")
        if self.options.with_tiff:
            self.requires("libtiff/4.1.0")
        if self.options.with_eigen:
            self.requires("eigen/3.3.7")
        if self.options.with_tbb:
            self.requires("tbb/2020.2")
        if self.options.with_webp:
            self.requires("libwebp/1.1.0")
        if self.options.contrib:
            self.requires("freetype/2.10.4")
            self.requires("harfbuzz/2.7.2")
            self.requires("gflags/2.2.2")
            self.requires("glog/0.4.0")
        if self.options.get_safe("with_gtk"):
            self.requires("gtk/system")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][0])
        os.rename("opencv-{}".format(self.version), self._source_subfolder)

        tools.get(**self.conan_data["sources"][self.version][1])
        os.rename("opencv_contrib-{}".format(self.version), self._contrib_folder)

    def _patch_opencv(self):
        tools.rmdir(os.path.join(self._source_subfolder, "3rdparty"))
        # allow to find conan-supplied OpenEXR
        if self.options.with_openexr:
            find_openexr = os.path.join(self._source_subfolder, "cmake", "OpenCVFindOpenEXR.cmake")
            tools.replace_in_file(find_openexr, "SET(OPENEXR_LIBSEARCH_SUFFIXES x64/Release x64 x64/Debug)", "")
            tools.replace_in_file(find_openexr, "SET(OPENEXR_LIBSEARCH_SUFFIXES Win32/Release Win32 Win32/Debug)", "")
            tools.replace_in_file(find_openexr, r'SET(OPENEXR_ROOT "C:/Deploy" CACHE STRING "Path to the OpenEXR \"Deploy\" folder")', "")

        tools.replace_in_file(os.path.join(self._source_subfolder, "data", "CMakeLists.txt"), "${OPENCV_OTHER_INSTALL_PATH}", "res")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "ANDROID OR NOT UNIX", "FALSE")
        tools.replace_in_file(os.path.join(self._source_subfolder, "modules", "imgcodecs", "CMakeLists.txt"), "JASPER_", "Jasper_")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_DOCS"] = False
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_PACKAGE"] = False
        self._cmake.definitions["BUILD_PERF_TESTS"] = False
        self._cmake.definitions["BUILD_opencv_apps"] = False
        self._cmake.definitions["BUILD_opencv_java"] = False
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

        self._cmake.definitions["WITH_CUFFT"] = False
        self._cmake.definitions["WITH_CUBLAS"] = False
        self._cmake.definitions["WITH_NVCUVID"] = False
        self._cmake.definitions["WITH_FFMPEG"] = False
        self._cmake.definitions["WITH_GSTREAMER"] = False
        self._cmake.definitions["WITH_OPENCL"] = False
        self._cmake.definitions["WITH_CUDA"] = False

        self._cmake.definitions["WITH_JPEG"] = self.options.with_jpeg
        self._cmake.definitions["WITH_PNG"] = self.options.with_png
        self._cmake.definitions["WITH_TIFF"] = self.options.with_tiff
        self._cmake.definitions["WITH_JASPER"] = self.options.with_jasper
        self._cmake.definitions["WITH_OPENEXR"] = self.options.with_openexr
        self._cmake.definitions["WITH_EIGEN"] = self.options.with_eigen
        self._cmake.definitions["WITH_TBB"] = self.options.with_tbb
        self._cmake.definitions["WITH_WEBP"] = self.options.with_webp
        self._cmake.definitions["WITH_IPP_IW"] = False
        self._cmake.definitions["WITH_IPP"] = False
        self._cmake.definitions["WITH_ITT"] = False
        self._cmake.definitions["WITH_CAROTENE"] = False
        self._cmake.definitions["WITH_QUIRC"] = False
        self._cmake.definitions["WITH_PROTOBUF"] = False # TODO: Add Protobuf
        self._cmake.definitions["WITH_LAPACK"] = False # TODO: Add LaPack
        self._cmake.definitions["WITH_DSHOW"] = self.settings.compiler == "Visual Studio"
        self._cmake.definitions["OPENCV_MODULES_PUBLIC"] = "opencv"
        self._cmake.definitions['WITH_GTK'] = self.options.get_safe("with_gtk", False)
        self._cmake.definitions['WITH_GTK_2_X'] = self.options.get_safe("with_gtk", False)

        if self.options.contrib:
            # OpenCV doesn't use find_package for freetype & harfbuzz, so let's specify them
            self._cmake.definitions['OPENCV_EXTRA_MODULES_PATH'] = os.path.join(self.build_folder, self._contrib_folder, 'modules')
            self._cmake.definitions['FREETYPE_FOUND'] = True
            self._cmake.definitions['FREETYPE_LIBRARIES'] = ';'.join(self.deps_cpp_info["freetype"].libs)
            self._cmake.definitions['FREETYPE_INCLUDE_DIRS'] = ';'.join(self.deps_cpp_info["freetype"].include_paths)
            self._cmake.definitions['HARFBUZZ_FOUND'] = True
            self._cmake.definitions['HARFBUZZ_LIBRARIES'] = ';'.join(self.deps_cpp_info["harfbuzz"].libs)
            self._cmake.definitions['HARFBUZZ_INCLUDE_DIRS'] = ';'.join(self.deps_cpp_info["harfbuzz"].include_paths)
            self._cmake.definitions['GFLAGS_LIBRARY_DIR_HINTS'] = ';'.join(self.deps_cpp_info["gflags"].lib_paths)
            self._cmake.definitions['GFLAGS_INCLUDE_DIR_HINTS'] = ';'.join(self.deps_cpp_info["gflags"].include_paths)
            self._cmake.definitions['GLOG_LIBRARY_DIR_HINTS'] = ';'.join(self.deps_cpp_info["glog"].lib_paths)
            self._cmake.definitions['GLOG_INCLUDE_DIR_HINTS'] = ';'.join(self.deps_cpp_info["glog"].include_paths)

        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["BUILD_WITH_STATIC_CRT"] = self.settings.compiler.runtime in ("MT", "MTd")
        if self.options.with_openexr:
            self._cmake.definitions['OPENEXR_ROOT'] = self.deps_cpp_info['openexr'].rootpath
        self._cmake.definitions["ENABLE_PIC"] = self.options.get_safe("fPIC", True)

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
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "staticlib"))
        tools.remove_files_by_mask(self.package_folder, "*.cmake")

    def package_info(self):
        version = self.version.split(".")[:-1]  # last version number is not used
        version = "".join(version) if self.settings.os == "Windows" else ""
        debug = "d" if self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio" else ""

        def get_lib_name(module):
            prefix = "" if module in ("correspondence", "multiview", "numeric") else "opencv_"
            return "%s%s%s%s" % (prefix, module, version, debug)

        def add_components(components):
            # TODO: OpenCV doesn't use cmake target namespace
            for component in components:
                conan_component = component["target"]
                cmake_target = component["target"]
                lib_name = get_lib_name(component["lib"])
                requires = component["requires"]
                self.cpp_info.components[conan_component].names["cmake_find_package"] = cmake_target
                self.cpp_info.components[conan_component].names["cmake_find_package_multi"] = cmake_target
                self.cpp_info.components[conan_component].libs = [lib_name]
                self.cpp_info.components[conan_component].requires = requires
                if self.settings.os == "Linux":
                    self.cpp_info.components[conan_component].system_libs = ["dl", "m", "pthread", "rt"]

                # CMake components names
                conan_component_alias = conan_component + "_alias"
                cmake_component = component["lib"]
                self.cpp_info.components[conan_component_alias].names["cmake_find_package"] = cmake_component
                self.cpp_info.components[conan_component_alias].names["cmake_find_package_multi"] = cmake_component
                self.cpp_info.components[conan_component_alias].requires = [conan_component]
                self.cpp_info.components[conan_component_alias].includedirs = []
                self.cpp_info.components[conan_component_alias].libdirs = []
                self.cpp_info.components[conan_component_alias].resdirs = []
                self.cpp_info.components[conan_component_alias].bindirs = []
                self.cpp_info.components[conan_component_alias].frameworkdirs = []

        def imageformats_deps():
            components = []
            if self.options.with_jasper:
                components.append("jasper::jasper")
            if self.options.with_png:
                components.append("libpng::libpng")
            if self.options.with_jpeg:
                components.append("libjpeg::libjpeg")
            if self.options.with_tiff:
                components.append("libtiff::libtiff")
            if self.options.with_openexr:
                components.append("openexr::openexr")
            if self.options.with_webp:
                components.append("libwebp::libwebp")
            return components

        def eigen():
            return ["eigen::eigen"] if self.options.with_eigen else []

        def tbb():
            return ["tbb::tbb"] if self.options.with_tbb else []

        def gtk():
            return ["gtk::gtk"] if self.options.get_safe("with_gtk") else []

        self.cpp_info.filenames["cmake_find_package"] = "OpenCV"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCV"

        add_components([
            {"target": "opencv_core",       "lib": "core",       "requires": ["zlib::zlib"] + eigen() + tbb()},
            {"target": "opencv_flann",      "lib": "flann",      "requires": ["opencv_core"] + eigen()},
            {"target": "opencv_imgproc",    "lib": "imgproc",    "requires": ["opencv_core"] + eigen()},
            {"target": "opencv_ml",         "lib": "ml",         "requires": ["opencv_core"] + eigen()},
            {"target": "opencv_photo",      "lib": "photo",      "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
            {"target": "opencv_video",      "lib": "video",      "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
            {"target": "opencv_features2d", "lib": "features2d", "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui"] + eigen()},
            {"target": "opencv_imgcodecs",  "lib": "imgcodecs",  "requires": ["opencv_core", "opencv_imgproc"] + eigen() + imageformats_deps()},
            {"target": "opencv_shape",      "lib": "shape",      "requires": ["opencv_core", "opencv_imgproc", "opencv_video"] + eigen()},
            {"target": "opencv_videoio",    "lib": "videoio",    "requires": ["opencv_core", "opencv_imgproc", "opencv_imgcodecs"] + eigen()},
            {"target": "opencv_calib3d",    "lib": "calib3d",    "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d"] + eigen()},
            {"target": "opencv_highgui",    "lib": "highgui",    "requires": ["opencv_core", "opencv_imgproc", "opencv_imgcodecs", "opencv_videoio"] + eigen() + gtk()},
            {"target": "opencv_objdetect",  "lib": "objdetect",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen()},
            {"target": "opencv_stitching",  "lib": "stitching",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen()},
            {"target": "opencv_superres",   "lib": "superres",   "requires": ["opencv_core", "opencv_imgproc", "opencv_video", "opencv_imgcodecs", "opencv_videoio"] + eigen()},
            {"target": "opencv_videostab",  "lib": "videostab",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_photo", "opencv_video", "opencv_features2d", "opencv_imgcodecs", "opencv_videoio", "opencv_calib3d"] + eigen()}
        ])

        if self.options.contrib:
            add_components([
                {"target": "opencv_phase_unwrapping", "lib": "phase_unwrapping", "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_plot",             "lib": "plot",             "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_reg",              "lib": "reg",              "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_surface_matching", "lib": "surface_matching", "requires": ["opencv_core", "opencv_flann"] + eigen()},
                {"target": "opencv_xphoto",           "lib": "xphoto",           "requires": ["opencv_core", "opencv_imgproc", "opencv_photo"] + eigen()},
                {"target": "opencv_freetype",         "lib": "freetype",         "requires": ["opencv_core", "opencv_imgproc", "freetype::freetype", "harfbuzz::harfbuzz"] + eigen()}, # TODO: Investigate
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
                {"target": "opencv_aruco",            "lib": "aruco",            "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d"] + eigen()},
                {"target": "opencv_bgsegm",           "lib": "bgsegm",           "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_video", "opencv_features2d", "opencv_calib3d"] + eigen()},
                {"target": "opencv_bioinspired",      "lib": "bioinspired",      "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_imgcodecs", "opencv_videoio", "opencv_highgui"] + eigen()},
                {"target": "opencv_ccalib",           "lib": "ccalib",           "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_videoio", "opencv_calib3d", "opencv_highgui"] + eigen()},
                {"target": "opencv_dpm",              "lib": "dpm",              "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_videoio", "opencv_calib3d", "opencv_highgui", "opencv_objdetect"] + eigen()},
                {"target": "opencv_face",             "lib": "face",             "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_photo", "opencv_video", "opencv_features2d", "opencv_calib3d", "opencv_objdetect"] + eigen()},
                {"target": "opencv_optflow",          "lib": "optflow",          "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_video", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d", "opencv_ximgproc"] + eigen()},
                {"target": "opencv_sfm",              "lib": "sfm",              "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_video", "opencv_features2d", "opencv_imgcodecs", "opencv_shape", "opencv_calib3d", "opencv_xfeatures2d", "correspondence", "multiview", "numeric", "glog::glog", "gflags::gflags"] + eigen()},

                {"target": "correspondence",          "lib": "correspondence",   "requires": ["glog::glog", "multiview"] + eigen()},
                {"target": "multiview",               "lib": "multiview",        "requires": ["glog::glog", "numeric"] + eigen()},
                {"target": "numeric",                 "lib": "numeric",          "requires": eigen()},
            ])

        if self.settings.os == "Windows":
            self.cpp_info.components["opencv_imgcodecs"].system_libs = ["comctl32", "gdi32", "ole32", "setupapi", "ws2_32", "vfw32"]
        elif self.settings.os == "Macos":
            self.cpp_info.components["opencv_imgcodecs"].frameworks = ['OpenCL', 'Accelerate', 'CoreMedia', 'CoreVideo', 'CoreGraphics', 'AVFoundation', 'QuartzCore', 'Cocoa']
