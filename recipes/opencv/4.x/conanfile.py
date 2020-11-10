from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.29.1"


class OpenCVConan(ConanFile):
    name = "opencv"
    license = "Apache"
    homepage = "https://opencv.org"
    description = "OpenCV (Open Source Computer Vision Library)"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("computer-vision", "deep-learning", "image-processing")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_jpeg": [True, False],
               "with_png": [True, False],
               "with_tiff": [True, False],
               "with_jasper": [True, False],
               "with_openexr": [True, False],
               "with_eigen": [True, False],
               "with_tbb": [True, False],
               "with_python2": [True, False],
               "with_python": [True, False],
               }
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_jpeg": True,
                       "with_png": True,
                       "with_tiff": False,
                       "with_jasper": False,
                       "with_openexr": False,
                       "with_eigen": True,
                       "with_tbb": False,
                       "with_python2": False,
                       "with_python": False,
                      }
    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler == "Visual Studio" and \
           "MT" in str(self.settings.compiler.runtime) and self.options.shared:
            raise ConanInvalidConfiguration("Visual Studio and Runtime MT is not supported for shared library.")
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        if self.settings.os == "Linux":
            self.build_requires("gtk/system")
            # self.build_requires("gtkmm/system")

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.with_jpeg:
            self.requires("libjpeg/9d")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_jasper:
            self.requires("jasper/2.0.21")
        if self.options.with_openexr:
            self.requires("openexr/2.5.3")
        if self.options.with_tiff:
            self.requires("libtiff/4.1.0")
        if self.options.with_eigen:
            self.requires("eigen/3.3.8")
        if self.options.with_tbb:
            self.requires("tbb/2020.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("opencv-{}".format(self.version), self._source_subfolder)

    def _patch_opencv(self):
        tools.rmdir(os.path.join(self._source_subfolder, "3rdparty"))

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

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
        self._cmake.definitions["BUILD_PACKAGE"] = False
        self._cmake.definitions["BUILD_PERF_TESTS"] = False
        self._cmake.definitions["BUILD_PNG"] = False
        self._cmake.definitions["BUILD_PROTOBUF"] = False
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["BUILD_TBB"] = False
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_TIFF"] = False
        self._cmake.definitions["BUILD_USE_SYMLINKS"] = False
        self._cmake.definitions["BUILD_WEBP"] = False
        self._cmake.definitions["BUILD_WITH_DYNAMIC_IPP"] = False
        self._cmake.definitions["BUILD_ZLIB"] = False

        self._cmake.definitions["BUILD_opencv_apps"] = False
        self._cmake.definitions["BUILD_opencv_java_bindings_gen"] = False
        self._cmake.definitions["BUILD_opencv_js"] = False
        self._cmake.definitions["BUILD_opencv_python2"] = self.options.with_python2
        self._cmake.definitions["BUILD_opencv_python3"] = self.options.with_python
        self._cmake.definitions["BUILD_opencv_python_bindings_g"] = self.options.with_python2 or self.options.with_python
        self._cmake.definitions["BUILD_opencv_python_tests"] = False

        self._cmake.definitions["ENABLE_PIC"] = self.options.get_safe("fPIC", True)

        self._cmake.definitions["WITH_1394"] = False
        self._cmake.definitions["WITH_ADE"] = False
        self._cmake.definitions["WITH_ARAVIS"] = False
        self._cmake.definitions["WITH_CLP"] = False
        self._cmake.definitions["WITH_CUDA"] = False
        self._cmake.definitions["WITH_EIGEN"] = self.options.with_eigen
        self._cmake.definitions["WITH_FFMPEG"] = False
        self._cmake.definitions["WITH_FREETYPE"] = False
        self._cmake.definitions["WITH_GDAL"] = False
        self._cmake.definitions["WITH_GDCM"] = False
        self._cmake.definitions["WITH_GPHOTO2"] = False
        self._cmake.definitions["WITH_GSTREAMER"] = False
        self._cmake.definitions["WITH_GTK"] = (self.settings.os == "Linux")
        self._cmake.definitions["WITH_GTK_2_X"] = False
        self._cmake.definitions["WITH_HALIDE"] = False
        self._cmake.definitions["WITH_HPX"] = False
        self._cmake.definitions["WITH_IMGCODEC_HDR"] = False
        self._cmake.definitions["WITH_IMGCODEC_PFM"] = False
        self._cmake.definitions["WITH_IMGCODEC_PXM"] = False
        self._cmake.definitions["WITH_IMGCODEC_SUNRASTER"] = False
        self._cmake.definitions["WITH_INF_ENGINE"] = False
        self._cmake.definitions["WITH_IPP"] = False
        self._cmake.definitions["WITH_ITT"] = False
        self._cmake.definitions["WITH_JASPER"] = self.options.with_jasper
        self._cmake.definitions["WITH_JPEG"] = self.options.with_jpeg
        self._cmake.definitions["WITH_LAPACK"] = False
        self._cmake.definitions["WITH_LIBREALSENSE"] = False
        self._cmake.definitions["WITH_MFX"] = False
        self._cmake.definitions["WITH_NGRAPH"] = False
        self._cmake.definitions["WITH_OPENCL"] = False
        self._cmake.definitions["WITH_OPENCLAMDBLAS"] = False
        self._cmake.definitions["WITH_OPENCLAMDFFT"] = False
        self._cmake.definitions["WITH_OPENCL_SVM"] = False
        self._cmake.definitions["WITH_OPENEXR"] = self.options.with_openexr
        self._cmake.definitions["WITH_OPENGL"] = False
        self._cmake.definitions["WITH_OPENJPEG"] = False
        self._cmake.definitions["WITH_OPENMP"] = False
        self._cmake.definitions["WITH_OPENNI"] = False
        self._cmake.definitions["WITH_OPENNI2"] = False
        self._cmake.definitions["WITH_OPENVX"] = False
        self._cmake.definitions["WITH_PLAIDML"] = False
        self._cmake.definitions["WITH_PNG"] = self.options.with_png
        self._cmake.definitions["WITH_PROTOBUF"] = False
        self._cmake.definitions["WITH_PTHREADS_PF"] = False
        self._cmake.definitions["WITH_PVAPI"] = False
        self._cmake.definitions["WITH_QT"] = False
        self._cmake.definitions["WITH_QUIRC"] = False
        self._cmake.definitions["WITH_TBB"] = self.options.with_tbb
        self._cmake.definitions["WITH_TIFF"] = self.options.with_tiff
        self._cmake.definitions["WITH_V4L"] = False
        self._cmake.definitions["WITH_VA"] = False
        self._cmake.definitions["WITH_VA_INTEL"] = False
        self._cmake.definitions["WITH_VTK"] = False
        self._cmake.definitions["WITH_VULKAN"] = False
        self._cmake.definitions["WITH_WEBP"] = False
        self._cmake.definitions["WITH_XIMEA"] = False
        self._cmake.definitions["WITH_XINE"] = False

        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["BUILD_WITH_STATIC_CRT"] = "MT" in str(self.settings.compiler.runtime)
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
            return "opencv_%s%s%s" % (module, version, debug)

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
                self.cpp_info.components[conan_component].includedirs = ['include/opencv4']
                self.cpp_info.components[conan_component].requires = requires
                if self.settings.os == "Linux":
                    self.cpp_info.components[conan_component].system_libs = ["dl", "m", "pthread", "rt"]

                if conan_component == 'opencv_highgui':
                    self.cpp_info.components[conan_component].system_libs = ["gtkmm-2.4"]

                # CMake components names
                conan_component_alias = conan_component + "_alias"
                cmake_component = component["lib"]
                self.cpp_info.components[conan_component_alias].names["cmake_find_package"] = cmake_component
                self.cpp_info.components[conan_component_alias].names["cmake_find_package_multi"] = cmake_component
                self.cpp_info.components[conan_component_alias].requires = [conan_component]
                self.cpp_info.components[conan_component_alias].includedirs = ['include/opencv4']
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
            return components

        def eigen():
            return ["eigen::eigen"] if self.options.with_eigen else []

        def tbb():
            return ["tbb::tbb"] if self.options.with_tbb else []

        self.cpp_info.filenames["cmake_find_package"] = "OpenCV"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCV"

        add_components([
            {"target": "opencv_core",       "lib": "core",       "requires": ["zlib::zlib"] + tbb()},
            {"target": "opencv_flann",      "lib": "flann",      "requires": ["opencv_core"]},
            {"target": "opencv_imgproc",    "lib": "imgproc",    "requires": ["opencv_core"]},
            {"target": "opencv_imgcodecs",  "lib": "imgcodecs",  "requires": ["opencv_core", "opencv_imgproc"]},
            {"target": "opencv_highgui",    "lib": "highgui",    "requires": ["opencv_core", "opencv_imgproc", "opencv_imgcodecs"] + eigen() + imageformats_deps()},
            {"target": "opencv_features2d", "lib": "features2d", "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui"]},
            {"target": "opencv_calib3d",    "lib": "calib3d",    "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d"]},
            {"target": "opencv_ml",         "lib": "ml",         "requires": ["opencv_core"]},
            {"target": "opencv_video",      "lib": "video",      "requires": ["opencv_core", "opencv_imgproc"]},
            {"target": "opencv_videoio",    "lib": "videoio",    "requires": ["opencv_core", "opencv_imgproc", "opencv_video"]},
            {"target": "opencv_objdetect",  "lib": "objdetect",  "requires": ["opencv_core", "opencv_imgproc", "opencv_highgui"]},
            {"target": "opencv_photo",      "lib": "photo",      "requires": ["opencv_core", "opencv_imgproc"]},
            {"target": "opencv_stitching",  "lib": "stitching",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_ml", "opencv_video", "opencv_objdetect", "opencv_photo"]},
        ])

        if self.settings.os == "Windows":
            self.cpp_info.components["opencv_highgui"].system_libs = ["comctl32", "gdi32", "ole32", "setupapi", "ws2_32", "vfw32"]
        elif self.settings.os == "Macos":
            self.cpp_info.components["opencv_highgui"].frameworks = ["Cocoa"]
