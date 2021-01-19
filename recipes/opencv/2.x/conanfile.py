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
               "with_jpeg": [True, False],
               "with_png": [True, False],
               "with_tiff": [True, False],
               "with_jasper": [True, False],
               "with_openexr": [True, False],
               "with_eigen": [True, False],
               "with_tbb": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_jpeg": True,
                       "with_png": True,
                       "with_tiff": True,
                       "with_jasper": True,
                       "with_openexr": True,
                       "with_eigen": True,
                       "with_tbb": False}
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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("opencv-{}".format(self.version), self._source_subfolder)

    def _patch_opencv(self):
        tools.rmdir(os.path.join(self._source_subfolder, "3rdparty"))
        # allow to find conan-supplied OpenEXR
        if self.options.with_openexr:
            find_openexr = os.path.join(self._source_subfolder, "cmake", "OpenCVFindOpenEXR.cmake")
            tools.replace_in_file(find_openexr,
                                  r'SET(OPENEXR_ROOT "C:/Deploy" CACHE STRING "Path to the OpenEXR \"Deploy\" folder")',
                                  "")
            tools.replace_in_file(find_openexr, r'set(OPENEXR_ROOT "")', "")
            tools.replace_in_file(find_openexr, "SET(OPENEXR_LIBSEARCH_SUFFIXES x64/Release x64 x64/Debug)", "")
            tools.replace_in_file(find_openexr, "SET(OPENEXR_LIBSEARCH_SUFFIXES Win32/Release Win32 Win32/Debug)", "")

            def openexr_library_names(name):
                # OpenEXR library may have different names, depends on namespace versioning, static, debug, etc.
                reference = str(self.requires["openexr"])
                version_name = reference.split("@")[0]
                version = version_name.split("/")[1]
                version_tokens = version.split(".")
                major, minor = version_tokens[0], version_tokens[1]
                suffix = "%s_%s" % (major, minor)
                names = ["%s-%s" % (name, suffix),
                         "%s-%s_s" % (name, suffix),
                         "%s-%s_d" % (name, suffix),
                         "%s-%s_s_d" % (name, suffix),
                         "%s" % name,
                         "%s_s" % name,
                         "%s_d" % name,
                         "%s_s_d" % name]
                return " ".join(names)

            for lib in ["Half", "Iex", "Imath", "IlmImf", "IlmThread"]:
                tools.replace_in_file(find_openexr, "NAMES %s" % lib, "NAMES %s" % openexr_library_names(lib))

            tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                "project(OpenCV CXX C)", "project(OpenCV CXX C)\nset(CMAKE_CXX_STANDARD 11)")

        for cascade in ["lbpcascades", "haarcascades"]:
            tools.replace_in_file(os.path.join(self._source_subfolder, "data", "CMakeLists.txt"),
                                  "share/OpenCV/%s" % cascade, "res/%s" % cascade)

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "staticlib", "lib")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "ANDROID OR NOT UNIX", "FALSE")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "${OpenCV_ARCH}/${OpenCV_RUNTIME}/", "")
        tools.replace_in_file(os.path.join(self._source_subfolder, "modules", "highgui", "CMakeLists.txt"), "JASPER_", "Jasper_")

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
        self._cmake.definitions["OPENCV_MODULES_PUBLIC"] = "opencv"

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
            return components

        def eigen():
            return ["eigen::eigen"] if self.options.with_eigen else []

        def tbb():
            return ["tbb::tbb"] if self.options.with_tbb else []

        self.cpp_info.filenames["cmake_find_package"] = "OpenCV"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCV"

        add_components([
            {"target": "opencv_core",       "lib": "core",       "requires": ["zlib::zlib"] + tbb()},
            {"target": "opencv_flann",      "lib": "flann",      "requires": ["opencv_core"] + tbb()},
            {"target": "opencv_imgproc",    "lib": "imgproc",    "requires": ["opencv_core"] + tbb()},
            {"target": "opencv_highgui",    "lib": "highgui",    "requires": ["opencv_core", "opencv_imgproc"] + eigen() + tbb() + imageformats_deps()},
            {"target": "opencv_features2d", "lib": "features2d", "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui"] + tbb()},
            {"target": "opencv_calib3d",    "lib": "calib3d",    "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d"] + tbb()},
            {"target": "opencv_ml",         "lib": "ml",         "requires": ["opencv_core"] + tbb()},
            {"target": "opencv_video",      "lib": "video",      "requires": ["opencv_core", "opencv_imgproc"] + tbb()},
            {"target": "opencv_legacy",     "lib": "legacy",     "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_ml", "opencv_video"] + eigen() + tbb()},
            {"target": "opencv_objdetect",  "lib": "objdetect",  "requires": ["opencv_core", "opencv_imgproc", "opencv_highgui"] + tbb()},
            {"target": "opencv_photo",      "lib": "photo",      "requires": ["opencv_core", "opencv_imgproc"] + tbb()},
            {"target": "opencv_gpu",        "lib": "gpu",        "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_ml", "opencv_video", "opencv_legacy", "opencv_objdetect", "opencv_photo"] + tbb()},
            {"target": "opencv_nonfree",    "lib": "nonfree",    "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_ml", "opencv_video", "opencv_legacy", "opencv_objdetect", "opencv_photo", "opencv_gpu"] + tbb()},
            {"target": "opencv_contrib",    "lib": "contrib",    "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_ml", "opencv_video", "opencv_legacy", "opencv_objdetect", "opencv_photo", "opencv_gpu", "opencv_nonfree"] + tbb()},
            {"target": "opencv_stitching",  "lib": "stitching",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_ml", "opencv_video", "opencv_legacy", "opencv_objdetect", "opencv_photo", "opencv_gpu", "opencv_nonfree"] + tbb()},
            {"target": "opencv_superres",   "lib": "superres",   "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_ml", "opencv_video", "opencv_legacy", "opencv_objdetect", "opencv_photo", "opencv_gpu"] + tbb()},
            {"target": "opencv_ts",         "lib": "ts",         "requires": ["opencv_core", "opencv_flann", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_video"] + tbb()},
            {"target": "opencv_videostab",  "lib": "videostab",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_ml", "opencv_video", "opencv_legacy", "opencv_objdetect", "opencv_photo", "opencv_gpu"] + tbb()}
        ])

        if self.settings.os == "Windows":
            self.cpp_info.components["opencv_highgui"].system_libs = ["comctl32", "gdi32", "ole32", "setupapi", "ws2_32", "vfw32"]
        elif self.settings.os == "Macos":
            self.cpp_info.components["opencv_highgui"].frameworks = ["Cocoa"]
