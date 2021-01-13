from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.29.1"


class OpenCVConan(ConanFile):
    name = "opencv"
    license = "Apache-2.0"
    homepage = "https://opencv.org"
    description = "OpenCV (Open Source Computer Vision Library)"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("computer-vision", "deep-learning", "image-processing")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "contrib": [True, False],
               "parallel": [False, "tbb", "openmp"],
               "with_jpeg": [False, "libjpeg", "libjpeg-turbo"],
               "with_png": [True, False],
               "with_tiff": [True, False],
               "with_jpeg2000": [False, "jasper", "openjpeg"],
               "with_openexr": [True, False],
               "with_eigen": [True, False],
               "with_webp": [True, False],
               "with_gtk": [True, False],
               "with_quirc": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "parallel": False,
                       "contrib": False,
                       "with_jpeg": "libjpeg",
                       "with_png": True,
                       "with_tiff": True,
                       "with_jpeg2000": "jasper",
                       "with_openexr": True,
                       "with_eigen": True,
                       "with_webp": True,
                       "with_gtk": True,
                       "with_quirc": True}
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
            del self.options.with_gtk

    def configure(self):
        if self.settings.compiler == "Visual Studio" and \
           "MT" in str(self.settings.compiler.runtime) and self.options.shared:
            raise ConanInvalidConfiguration("Visual Studio and Runtime MT is not supported for shared library.")
        if self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) < "4":
            raise ConanInvalidConfiguration("Clang 3.x can build OpenCV 4.x due an internal bug.")
        if self.options.shared:
            del self.options.fPIC
        self.options["libtiff"].jpeg = self.options.with_jpeg
        self.options["jasper"].with_libjpeg = self.options.with_jpeg

        if self.settings.os == "Android":
            self.options.with_openexr = False  # disabled because this forces linkage to libc++_shared.so

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9d")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.0.5")
        if self.options.with_jpeg2000 == "jasper":
            self.requires("jasper/2.0.21")
        elif self.options.with_jpeg2000 == "openjpeg":
            self.requires("openjpeg/2.3.1")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_openexr:
            self.requires("openexr/2.5.3")
        if self.options.with_tiff:
            self.requires("libtiff/4.1.0")
        if self.options.with_eigen:
            self.requires("eigen/3.3.8")
        if self.options.parallel == "tbb":
            self.requires("tbb/2020.2")
        if self.options.with_webp:
            self.requires("libwebp/1.1.0")
        if self.options.contrib:
            self.requires("freetype/2.10.4")
            self.requires("harfbuzz/2.7.2")
            self.requires("gflags/2.2.2")
            self.requires("glog/0.4.0")
        if self.options.with_quirc:
            self.requires("quirc/1.1")
        if self.options.get_safe("with_gtk"):
            self.requires("gtk/system")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][0])
        os.rename("opencv-{}".format(self.version), self._source_subfolder)

        tools.get(**self.conan_data["sources"][self.version][1])
        os.rename("opencv_contrib-{}".format(self.version), self._contrib_folder)

    def _patch_opencv(self):
        for directory in ['libjasper', 'libjpeg-turbo', 'libjpeg', 'libpng', 'libtiff', 'libwebp', 'openexr', 'protobuf', 'zlib', 'quirc']:
            tools.rmdir(os.path.join(self._source_subfolder, '3rdparty', directory))
        if self.options.with_openexr:
            find_openexr = os.path.join(self._source_subfolder, "cmake", "OpenCVFindOpenEXR.cmake")
            tools.replace_in_file(find_openexr,
                                  r'SET(OPENEXR_ROOT "C:/Deploy" CACHE STRING "Path to the OpenEXR \"Deploy\" folder")',
                                  "")
            tools.replace_in_file(find_openexr, "SET(OPENEXR_LIBSEARCH_SUFFIXES x64/Release x64 x64/Debug)", "")
            tools.replace_in_file(find_openexr, "SET(OPENEXR_LIBSEARCH_SUFFIXES Win32/Release Win32 Win32/Debug)", "")

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "ANDROID OR NOT UNIX", "FALSE")
        tools.replace_in_file(os.path.join(self._source_subfolder, "modules", "imgcodecs", "CMakeLists.txt"), "JASPER_", "Jasper_")

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
        self._cmake.definitions["BUILD_opencv_python2"] = False
        self._cmake.definitions["BUILD_opencv_python3"] = False
        self._cmake.definitions["BUILD_opencv_python_bindings_g"] = False
        self._cmake.definitions["BUILD_opencv_python_tests"] = False
        self._cmake.definitions["BUILD_opencv_ts"] = False

        self._cmake.definitions["WITH_1394"] = False
        self._cmake.definitions["WITH_ADE"] = False
        self._cmake.definitions["WITH_ARAVIS"] = False
        self._cmake.definitions["WITH_CLP"] = False
        self._cmake.definitions["WITH_CUDA"] = False
        self._cmake.definitions["WITH_CUFFT"] = False
        self._cmake.definitions["WITH_CUBLAS"] = False
        self._cmake.definitions["WITH_NVCUVID"] = False
        self._cmake.definitions["WITH_FFMPEG"] = False
        self._cmake.definitions["WITH_GSTREAMER"] = False
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
        self._cmake.definitions["WITH_OPENCL"] = False
        self._cmake.definitions["WITH_OPENCLAMDBLAS"] = False
        self._cmake.definitions["WITH_OPENCLAMDFFT"] = False
        self._cmake.definitions["WITH_OPENCL_SVM"] = False
        self._cmake.definitions["WITH_OPENGL"] = False
        self._cmake.definitions["WITH_OPENJPEG"] = False
        self._cmake.definitions["WITH_OPENMP"] = False
        self._cmake.definitions["WITH_OPENNI"] = False
        self._cmake.definitions["WITH_OPENNI2"] = False
        self._cmake.definitions["WITH_OPENVX"] = False
        self._cmake.definitions["WITH_PLAIDML"] = False
        self._cmake.definitions["WITH_PROTOBUF"] = False
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

        self._cmake.definitions["WITH_GTK"] = self.options.get_safe("with_gtk", False)
        self._cmake.definitions["WITH_GTK_2_X"] = self.options.get_safe("with_gtk", False)
        self._cmake.definitions["WITH_WEBP"] = self.options.with_webp
        self._cmake.definitions["WITH_JPEG"] = self.options.with_jpeg != False
        self._cmake.definitions["WITH_PNG"] = self.options.with_png
        self._cmake.definitions["WITH_TIFF"] = self.options.with_tiff
        self._cmake.definitions["WITH_JASPER"] = self.options.with_jpeg2000 == "jasper"
        self._cmake.definitions["WITH_OPENJPEG"] = self.options.with_jpeg2000 == "openjpeg"
        self._cmake.definitions["WITH_OPENEXR"] = self.options.with_openexr
        self._cmake.definitions["WITH_EIGEN"] = self.options.with_eigen
        self._cmake.definitions["HAVE_QUIRC"] = self.options.with_quirc  # force usage of quirc requirement
        self._cmake.definitions["WITH_DSHOW"] = self.settings.compiler == "Visual Studio"
        self._cmake.definitions["WITH_MSMF"] = self.settings.compiler == "Visual Studio"
        self._cmake.definitions["WITH_MSMF_DXVA"] = self.settings.compiler == "Visual Studio"
        self._cmake.definitions["OPENCV_MODULES_PUBLIC"] = "opencv"
        if self.options.contrib:
            self._cmake.definitions['OPENCV_EXTRA_MODULES_PATH'] = os.path.join(self.build_folder, self._contrib_folder, 'modules')
        if self.options.with_openexr:
            self._cmake.definitions["OPENEXR_ROOT"] = self.deps_cpp_info["openexr"].rootpath
        if self.options.with_jpeg2000 == "openjpeg":
            openjpeg_version = tools.Version(self.deps_cpp_info["openjpeg"].version)
            self._cmake.definitions["OPENJPEG_MAJOR_VERSION"] = openjpeg_version.major
            self._cmake.definitions["OPENJPEG_MINOR_VERSION"] = openjpeg_version.minor
            self._cmake.definitions["OPENJPEG_BUILD_VERSION"] = openjpeg_version.patch
        if self.options.parallel:
            self._cmake.definitions["WITH_TBB"] = self.options.parallel == "tbb"
            self._cmake.definitions["WITH_OPENMP"] = self.options.parallel == "openmp"

        self._cmake.definitions["ENABLE_PIC"] = self.options.get_safe("fPIC", True)

        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["BUILD_WITH_STATIC_CRT"] = "MT" in str(self.settings.compiler.runtime)

        if self.settings.os == "Android":
            self._cmake.definitions["ANDROID_STL"] = "c++_static"
            self._cmake.definitions["ANDROID_NATIVE_API_LEVEL"] = self.settings.os.api_level
            self._cmake.definitions["ANDROID_ABI"] = tools.to_android_abi(str(self.settings.arch))
            self._cmake.definitions["BUILD_ANDROID_EXAMPLES"] = False
            if "ANDROID_NDK_HOME" in os.environ:
                self._cmake.definitions["ANDROID_NDK"] = os.environ.get("ANDROID_NDK_HOME")

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
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        if os.path.isfile(os.path.join(self.package_folder, "setup_vars_opencv4.cmd")):
            os.rename(os.path.join(self.package_folder, "setup_vars_opencv4.cmd"),
                      os.path.join(self.package_folder, "res", "setup_vars_opencv4.cmd"))

    def package_info(self):
        version = self.version.split(".")
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
                            os.path.join("sdk", "native", "staticlibs", tools.to_android_abi(str(self.settings.arch))))
                        if conan_component == "opencv_core":
                            self.cpp_info.components[conan_component].libdirs.append("lib")
                            self.cpp_info.components[conan_component].libs += tools.collect_libs(self)

                if self.settings.os == "iOS":
                    if not self.options.shared:
                        if conan_component == "opencv_core":
                            libs = list(filter(lambda x: not x.startswith("opencv"), tools.collect_libs(self)))
                            self.cpp_info.components[conan_component].libs += libs

                # CMake components names
                conan_component_alias = conan_component + "_alias"
                cmake_component = component["lib"]
                self.cpp_info.components[conan_component_alias].names["cmake_find_package"] = cmake_component
                self.cpp_info.components[conan_component_alias].names["cmake_find_package_multi"] = cmake_component
                self.cpp_info.components[conan_component_alias].requires = [conan_component]
                self.cpp_info.components[conan_component_alias].includedirs.append(os.path.join("include", "opencv4"))
                self.cpp_info.components[conan_component_alias].libdirs = []
                self.cpp_info.components[conan_component_alias].resdirs = []
                self.cpp_info.components[conan_component_alias].bindirs = []
                self.cpp_info.components[conan_component_alias].frameworkdirs = []

        def imageformats_deps():
            components = []
            if self.options.with_jpeg2000:
                components.append("{0}::{0}".format(self.options.with_jpeg2000))
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
                return ["tbb::tbb"] if self.options.parallel == "tbb" else ["openmp"]
            return []

        def quirc():
            return ["quirc::quirc"] if self.options.with_quirc else []

        def gtk():
            return ["gtk::gtk"] if self.options.get_safe("with_gtk") else []

        def freetype():
            return ["freetype::freetype"] if self.options.contrib else []

        def xfeatures2d():
            return ["opencv_xfeatures2d"] if self.options.contrib else []

        self.cpp_info.filenames["cmake_find_package"] = "OpenCV"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCV"

        add_components([
            {"target": "opencv_core",       "lib": "core",       "requires": ["zlib::zlib"] + parallel() + eigen()},
            {"target": "opencv_flann",      "lib": "flann",      "requires": ["opencv_core"] + eigen()},
            {"target": "opencv_imgproc",    "lib": "imgproc",    "requires": ["opencv_core"] + eigen()},
            {"target": "opencv_ml",         "lib": "ml",         "requires": ["opencv_core"] + eigen()},
            {"target": "opencv_photo",      "lib": "photo",      "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
            {"target": "opencv_features2d", "lib": "features2d", "requires": ["opencv_core", "opencv_flann", "opencv_imgproc"] + eigen()},
            {"target": "opencv_imgcodecs",  "lib": "imgcodecs",  "requires": ["opencv_core", "opencv_imgproc", "zlib::zlib"] + eigen() + imageformats_deps()},
            {"target": "opencv_videoio",    "lib": "videoio",    "requires": ["opencv_core", "opencv_imgproc", "opencv_imgcodecs"] + eigen()},
            {"target": "opencv_calib3d",    "lib": "calib3d",    "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d"]+ eigen()},
            {"target": "opencv_highgui",    "lib": "highgui",    "requires": ["opencv_core", "opencv_imgproc", "opencv_imgcodecs", "opencv_videoio"] + freetype() + eigen() + gtk()},
            {"target": "opencv_objdetect",  "lib": "objdetect",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen() + quirc()},
            {"target": "opencv_stitching",  "lib": "stitching",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + xfeatures2d() + eigen()},
            {"target": "opencv_video",      "lib": "video",      "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen()},
        ])

        if self.options.contrib:
            add_components([
                {"target": "opencv_intensity_transform", "lib": "intensity_transform", "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_phase_unwrapping",    "lib": "phase_unwrapping",    "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_plot",                "lib": "plot",                "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_quality",             "lib": "quality",             "requires": ["opencv_core", "opencv_imgproc", "opencv_ml"] + eigen()},
                {"target": "opencv_reg",                 "lib": "reg",                 "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_surface_matching",    "lib": "surface_matching",    "requires": ["opencv_core", "opencv_flann"] + eigen()},
                {"target": "opencv_xphoto",              "lib": "xphoto",              "requires": ["opencv_core", "opencv_imgproc", "opencv_photo"] + eigen()},
                {"target": "opencv_alphamat",            "lib": "alphamat",            "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_freetype",            "lib": "freetype",            "requires": ["opencv_core", "opencv_imgproc", "freetype::freetype", "harfbuzz::harfbuzz"] + eigen()},
                {"target": "opencv_fuzzy",               "lib": "fuzzy",               "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_hfs",                 "lib": "hfs",                 "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_img_hash",            "lib": "img_hash",            "requires": ["opencv_core", "opencv_imgproc"] + eigen()},
                {"target": "opencv_line_descriptor",     "lib": "line_descriptor",     "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d"] + eigen()},
                {"target": "opencv_saliency",            "lib": "saliency",            "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d"] + eigen()},
                {"target": "opencv_datasets",            "lib": "datasets",            "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_imgcodecs"] + eigen()},
                {"target": "opencv_rapid",               "lib": "rapid",               "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen()},
                {"target": "opencv_rgbd",                "lib": "rgbd",                "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen()},
                {"target": "opencv_shape",               "lib": "shape",               "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d"] + eigen()},
                {"target": "opencv_structured_light",    "lib": "structured_light",    "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_phase_unwrapping", "opencv_features2d", "opencv_calib3d"] + eigen()},
                {"target": "opencv_videostab",           "lib": "videostab",           "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_photo", "opencv_features2d", "opencv_imgcodecs", "opencv_videoio", "opencv_calib3d", "opencv_video"] + eigen()},
                {"target": "opencv_xfeatures2d",         "lib": "xfeatures2d",         "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_features2d", "opencv_calib3d", "opencv_shape", ] + eigen()},
                {"target": "opencv_ximgproc",            "lib": "ximgproc",            "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d", "opencv_video"] + eigen()},
                {"target": "opencv_xobjdetect",          "lib": "xobjdetect",          "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d", "opencv_objdetect"] + eigen()},
                {"target": "opencv_aruco",               "lib": "aruco",               "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d"] + eigen()},
                {"target": "opencv_bgsegm",              "lib": "bgsegm",              "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_calib3d", "opencv_video"] + eigen()},
                {"target": "opencv_bioinspired",         "lib": "bioinspired",         "requires": ["opencv_core", "opencv_imgproc", "opencv_imgcodecs", "opencv_videoio", "opencv_highgui"] + eigen()},
                {"target": "opencv_ccalib",              "lib": "ccalib",              "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_videoio", "opencv_calib3d", "opencv_highgui"] + eigen()},
                {"target": "opencv_dpm",                 "lib": "dpm",                 "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_videoio", "opencv_calib3d", "opencv_highgui", "opencv_objdetect"] + eigen()},
                {"target": "opencv_face",                "lib": "face",                "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_photo", "opencv_features2d", "opencv_calib3d", "opencv_objdetect"] + eigen()},
                {"target": "opencv_optflow",             "lib": "optflow",             "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_video", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d", "opencv_video", "opencv_ximgproc"] + eigen()},
                {"target": "opencv_sfm",                 "lib": "sfm",                 "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d", "opencv_shape", "opencv_xfeatures2d", "correspondence", "multiview", "numeric", "glog::glog", "gflags::gflags"] + eigen()},
                {"target": "correspondence",             "lib": "correspondence",      "requires": ["glog::glog", "multiview"] + eigen()},
                {"target": "multiview",                  "lib": "multiview",           "requires": ["glog::glog", "numeric"] + eigen()},
                {"target": "numeric",                    "lib": "numeric",             "requires": eigen()},
                {"target": "opencv_superres",            "lib": "superres",            "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_features2d", "opencv_imgcodecs", "opencv_videoio", "opencv_calib3d", "opencv_video", "opencv_ximgproc", "opencv_optflow"] + eigen()},
                {"target": "opencv_tracking",            "lib": "tracking",            "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_plot", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d", "opencv_datasets", "opencv_video"] + eigen()},
                {"target": "opencv_stereo",              "lib": "stereo",              "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_ml", "opencv_plot", "opencv_features2d", "opencv_imgcodecs", "opencv_calib3d", "opencv_datasets", "opencv_video", "opencv_tracking"] + eigen()},
            ])

        if self.settings.os == "Windows":
            self.cpp_info.components["opencv_highgui"].system_libs = ["comctl32", "gdi32", "ole32", "setupapi", "ws2_32", "vfw32"]
        elif self.settings.os == "Macos":
            self.cpp_info.components["opencv_highgui"].frameworks = ["Cocoa"]
            self.cpp_info.components["opencv_videoio"].frameworks = ["Cocoa", "Accelerate", "AVFoundation", "CoreGraphics", "CoreMedia", "CoreVideo", "QuartzCore"]
        elif self.settings.os == "iOS":
            self.cpp_info.components["opencv_videoio"].frameworks = ["AVFoundation", "QuartzCore"]
