from conans import ConanFile, CMake, tools
import os


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
               "with_openexr": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_jpeg": True,
                       "with_png": True,
                       "with_tiff": True,
                       "with_jasper": True,
                       "with_openexr": True}
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
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
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("gtk2/system")

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.with_jpeg:
            self.requires("libjpeg/9d")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_jasper:
            self.requires("jasper/2.0.19")
        if self.options.with_openexr:
            self.requires("openexr/2.5.2")
        if self.options.with_tiff:
            self.requires("libtiff/4.1.0")

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

        for cascade in ["lbpcascades", "haarcascades"]:
            tools.replace_in_file(os.path.join(self._source_subfolder, "data", "CMakeLists.txt"),
                                  "share/OpenCV/%s" % cascade, "res/%s" % cascade)

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
        self._cmake.definitions["WITH_ZLIB"] = True

        self._cmake.definitions["WITH_JPEG"] = self.options.with_jpeg
        self._cmake.definitions["WITH_PNG"] = self.options.with_png
        self._cmake.definitions["WITH_TIFF"] = self.options.with_tiff
        self._cmake.definitions["WITH_JASPER"] = self.options.with_jasper
        self._cmake.definitions["WITH_OPENEXR"] = self.options.with_openexr
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

    def package_info(self):
        version = self.version.split(".")[:-1]  # last version number is not used
        version = "".join(version) if self.settings.os == "Windows" else ""
        debug = "d" if self.settings.build_type == "Debug" and self.settings.compiler == "Visual Studio" else ""

        def get_lib_name(module):
            return "opencv_%s%s%s" % (module, version, debug)

        def add_components(components):
            # TODO: OpenCV doesn't use cmake target namespace
            for component, requires in components.items():
                self.cpp_info.components[component].names["cmake_find_package"] = "opencv_" + component
                self.cpp_info.components[component].names["cmake_find_package_multi"] = "opencv_" + component
                self.cpp_info.components[component].libs = [get_lib_name(component)]
                self.cpp_info.components[component].requires = requires
                if self.settings.os == "Linux":
                    self.cpp_info.components[component].system_libs = ["dl", "m", "pthread", "rt"]

        if self.settings.compiler == "Visual Studio":
            libdir = "lib" if self.options.shared else "staticlib"
            arch = {"x86": "x86",
                    "x86_64": "x64"}.get(str(self.settings.arch))
            if self.settings.compiler.version == "12":
                libdir = os.path.join(self.package_folder, arch, "vc12", libdir)
                bindir = os.path.join(self.package_folder, arch, "vc12", "bin")
            elif self.settings.compiler.version == "14":
                libdir = os.path.join(self.package_folder, arch, "vc14", libdir)
                bindir = os.path.join(self.package_folder, arch, "vc14", "bin")
            else:
                libdir = os.path.join(self.package_folder, libdir)
                bindir = os.path.join(self.package_folder, "bin")
            self.cpp_info.bindirs.append(bindir)
            self.cpp_info.libdirs.append(libdir)

        self.cpp_info.filenames["cmake_find_package"] = "OpenCV"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCV"

        add_components({
            "core": ["zlib::zlib"],
            "flann": ["core"],
            "imgproc": ["core"],
            "highgui": ["core", "imgproc", "jasper::jasper", "zlib::zlib", "libpng::libpng", "libjpeg::libjpeg", "libtiff::libtiff", "jasper::jasper", "openexr::openexr"],
            "features2d": ["core", "flann", "imgproc", "highgui"],
            "calib3d": ["core", "flann", "imgproc", "highgui", "features2d"],
            "ml": ["core"],
            "video": ["core", "imgproc"],
            "legacy": ["core", "flann", "imgproc", "highgui", "features2d", "calib3d", "ml", "video"],
            "objdetect": ["core", "imgproc", "highgui"],
            "photo": ["core", "imgproc"],
            "gpu": ["core", "flann", "imgproc", "highgui", "features2d", "calib3d", "ml", "video", "legacy", "objdetect", "photo"],
            "nonfree": ["core", "flann", "imgproc", "highgui", "features2d", "calib3d", "ml", "video", "legacy", "objdetect", "photo", "gpu"],
            "contrib": ["core", "flann", "imgproc", "highgui", "features2d", "calib3d", "ml", "video", "legacy", "objdetect", "photo", "gpu", "nonfree"],
            "stitching": ["core", "flann", "imgproc", "highgui", "features2d", "calib3d", "ml", "video", "legacy", "objdetect", "photo", "gpu", "nonfree"],
            "superres": ["core", "flann", "imgproc", "highgui", "features2d", "calib3d", "ml", "video", "legacy", "objdetect", "photo", "gpu"],
            "ts": ["core", "flann", "highgui", "features2d", "calib3d", "video"],
            "videostab": ["core", "flann", "imgproc", "highgui", "features2d", "calib3d", "ml", "video", "legacy", "objdetect", "photo", "gpu"]
        })

        if self.settings.os == "Macos":
            self.cpp_info.components["highgui"].frameworks = ["Cocoa"]
