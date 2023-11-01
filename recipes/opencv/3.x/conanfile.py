from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, replace_in_file, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.54.0"


class OpenCVConan(ConanFile):
    name = "opencv"
    license = "BSD-3-Clause"
    homepage = "https://opencv.org"
    description = "OpenCV (Open Source Computer Vision Library)"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("computer-vision", "deep-learning", "image-processing")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "contrib": [True, False],
        "parallel": [False, "tbb", "openmp"],
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo", "mozjpeg"],
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

    @property
    def _contrib_folder(self):
        return os.path.join(self.source_folder, "contrib")

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_gtk

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["*"].jpeg = self.options.with_jpeg
        self.options["*"].with_libjpeg = self.options.with_jpeg
        self.options["*"].with_jpeg = self.options.with_jpeg

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.0")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.3")
        if self.options.with_png:
            self.requires("libpng/1.6.40")
        if self.options.with_jasper:
            self.requires("jasper/4.0.0")
        if self.options.with_openexr:
            # opencv 3.x doesn't support openexr >= 3
            self.requires("openexr/2.5.7")
        if self.options.with_tiff:
            self.requires("libtiff/4.6.0")
        if self.options.with_eigen:
            self.requires("eigen/3.4.0")
        if self.options.parallel == "tbb":
            # opencv 3.x doesn't support onetbb >= 2021
            self.requires("onetbb/2020.3.3")
        if self.options.with_webp:
            self.requires("libwebp/1.3.2")
        if self.options.contrib:
            self.requires("freetype/2.13.0")
            self.requires("harfbuzz/8.2.2")
            self.requires("gflags/2.2.2")
            self.requires("glog/0.6.0")
        if self.options.get_safe("with_gtk"):
            self.requires("gtk/system")

    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio with static runtime is not supported for shared library.")
        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "4":
            raise ConanInvalidConfiguration("Clang 3.x cannot build OpenCV 3.x due an internal bug.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version][0], strip_root=True)

        get(self, **self.conan_data["sources"][self.version][1],
            destination=self._contrib_folder, strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)
        rmdir(self, os.path.join(self.source_folder, "3rdparty"))
        if self.options.contrib:
            freetype_cmake = os.path.join(self._contrib_folder, "modules", "freetype", "CMakeLists.txt")
            replace_in_file(self, freetype_cmake, "ocv_check_modules(FREETYPE freetype2)", "find_package(Freetype REQUIRED MODULE)")
            replace_in_file(self, freetype_cmake, "FREETYPE_", "Freetype_")

            replace_in_file(self, freetype_cmake, "ocv_check_modules(HARFBUZZ harfbuzz)", "find_package(harfbuzz REQUIRED)")
            replace_in_file(self, freetype_cmake, "HARFBUZZ_", "harfbuzz_")

        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "ANDROID OR NOT UNIX", "FALSE")
        replace_in_file(self, os.path.join(self.source_folder, "modules", "imgcodecs", "CMakeLists.txt"), "JASPER_", "Jasper_")

        # Cleanup RPATH
        install_layout_file = os.path.join(self.source_folder, "cmake", "OpenCVInstallLayout.cmake")
        replace_in_file(self, install_layout_file,
                              "ocv_update(CMAKE_INSTALL_RPATH \"${CMAKE_INSTALL_PREFIX}/${OPENCV_LIB_INSTALL_PATH}\")",
                              "")
        replace_in_file(self, install_layout_file, "set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)", "")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OPENCV_CONFIG_INSTALL_PATH"] = "cmake"
        tc.variables["OPENCV_BIN_INSTALL_PATH"] = "bin"
        tc.variables["OPENCV_LIB_INSTALL_PATH"] = "lib"
        tc.variables["OPENCV_3P_LIB_INSTALL_PATH"] = "lib"
        tc.variables["OPENCV_OTHER_INSTALL_PATH"] = "res"
        tc.variables["OPENCV_LICENSES_INSTALL_PATH"] = "licenses"
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_DOCS"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_PACKAGE"] = False
        tc.variables["BUILD_PERF_TESTS"] = False
        tc.variables["BUILD_JAVA"] = False
        tc.variables["BUILD_FAT_JAVA_LIB"] = False
        tc.variables["BUILD_PERF_TESTS"] = False
        tc.variables["BUILD_ZLIB"] = False
        tc.variables["BUILD_JPEG"] = False
        tc.variables["BUILD_PNG"] = False
        tc.variables["BUILD_TIFF"] = False
        tc.variables["BUILD_JASPER"] = False
        tc.variables["BUILD_OPENEXR"] = False
        tc.variables["BUILD_WEBP"] = False
        tc.variables["BUILD_TBB"] = False
        tc.variables["BUILD_JPEG_TURBO_DISABLE"] = True
        tc.variables["BUILD_IPP_IW"] = False
        tc.variables["BUILD_ITT"] = False
        tc.variables["BUILD_PROTOBUF"] = False
        tc.variables["BUILD_USE_SYMLINKS"] = False
        tc.variables["OPENCV_FORCE_3RDPARTY_BUILD"] = False
        tc.variables["BUILD_opencv_java_bindings_gen"] = False
        tc.variables["BUILD_opencv_js"] = False
        tc.variables["BUILD_opencv_apps"] = False
        tc.variables["BUILD_opencv_java"] = False
        tc.variables["OPENCV_PYTHON_SKIP_DETECTION"] = True
        tc.variables["BUILD_opencv_python2"] = False
        tc.variables["BUILD_opencv_python3"] = False
        tc.variables["BUILD_opencv_python_bindings_g"] = False
        tc.variables["BUILD_opencv_python_tests"] = False
        tc.variables["BUILD_opencv_ts"] = False
        tc.variables["WITH_CUFFT"] = False
        tc.variables["WITH_CUBLAS"] = False
        tc.variables["WITH_NVCUVID"] = False
        tc.variables["WITH_FFMPEG"] = False
        tc.variables["WITH_GSTREAMER"] = False
        tc.variables["WITH_OPENCL"] = False
        tc.variables["WITH_CUDA"] = False
        tc.variables["WITH_1394"] = False
        tc.variables["WITH_ADE"] = False
        tc.variables["WITH_ARAVIS"] = False
        tc.variables["WITH_CLP"] = False
        tc.variables["WITH_HALIDE"] = False
        tc.variables["WITH_HPX"] = False
        tc.variables["WITH_IMGCODEC_HDR"] = False
        tc.variables["WITH_IMGCODEC_PFM"] = False
        tc.variables["WITH_IMGCODEC_PXM"] = False
        tc.variables["WITH_IMGCODEC_SUNRASTER"] = False
        tc.variables["WITH_INF_ENGINE"] = False
        tc.variables["WITH_IPP"] = False
        tc.variables["WITH_ITT"] = False
        tc.variables["WITH_LIBREALSENSE"] = False
        tc.variables["WITH_MFX"] = False
        tc.variables["WITH_NGRAPH"] = False
        tc.variables["WITH_OPENCLAMDBLAS"] = False
        tc.variables["WITH_OPENCLAMDFFT"] = False
        tc.variables["WITH_OPENCL_SVM"] = False
        tc.variables["WITH_OPENGL"] = False
        tc.variables["WITH_OPENNI"] = False
        tc.variables["WITH_OPENNI2"] = False
        tc.variables["WITH_OPENVX"] = False
        tc.variables["WITH_PLAIDML"] = False
        tc.variables["WITH_PROTOBUF"] = False
        tc.variables["WITH_PTHREADS_PF"] = False
        tc.variables["WITH_PVAPI"] = False
        tc.variables["WITH_QT"] = False
        tc.variables["WITH_QUIRC"] = False
        tc.variables["WITH_V4L"] = False
        tc.variables["WITH_VA"] = False
        tc.variables["WITH_VA_INTEL"] = False
        tc.variables["WITH_VTK"] = False
        tc.variables["WITH_VULKAN"] = False
        tc.variables["WITH_XIMEA"] = False
        tc.variables["WITH_XINE"] = False
        tc.variables["WITH_LAPACK"] = False
        tc.variables["WITH_IPP_IW"] = False
        tc.variables["WITH_CAROTENE"] = False
        tc.variables["WITH_PROTOBUF"] = False
        tc.variables["WITH_LAPACK"] = False
        tc.variables["WITH_JPEG"] = bool(self.options.with_jpeg)
        tc.variables["WITH_PNG"] = self.options.with_png
        tc.variables["WITH_TIFF"] = self.options.with_tiff
        tc.variables["WITH_JASPER"] = self.options.with_jasper
        tc.variables["WITH_OPENEXR"] = self.options.with_openexr
        if self.options.with_openexr:
            tc.variables["CMAKE_CXX_STANDARD"] = 11
        tc.variables["WITH_EIGEN"] = self.options.with_eigen
        tc.variables["WITH_WEBP"] = self.options.with_webp
        tc.variables["WITH_DSHOW"] = is_msvc(self)
        tc.variables["WITH_MSMF"] = is_msvc(self)
        tc.variables["WITH_MSMF_DXVA"] = is_msvc(self)
        tc.variables["WITH_GTK"] = self.options.get_safe("with_gtk", False)
        tc.variables["WITH_GTK_2_X"] = self.options.get_safe("with_gtk", False)
        tc.variables["OPENCV_MODULES_PUBLIC"] = "opencv"
        tc.variables["OPENCV_ENABLE_NONFREE"] = self.options.nonfree
        if self.options.parallel:
            tc.variables["WITH_TBB"] = self.options.parallel == "tbb"
            tc.variables["WITH_OPENMP"] = self.options.parallel == "openmp"
        if self.options.contrib:
            tc.variables["OPENCV_EXTRA_MODULES_PATH"] = os.path.join(self._contrib_folder, "modules").replace("\\", "/")
        if is_msvc(self):
            tc.variables["BUILD_WITH_STATIC_CRT"] = is_msvc_static_runtime(self)
        tc.variables["ENABLE_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["ENABLE_CCACHE"] = False
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
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        if os.path.isfile(os.path.join(self.package_folder, "setup_vars_opencv3.cmd")):
            rename(self, os.path.join(self.package_folder, "setup_vars_opencv3.cmd"),
                         os.path.join(self.package_folder, "res", "setup_vars_opencv3.cmd"))

        self._create_cmake_module_variables(os.path.join(self.package_folder, self._module_vars_rel_path))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_target_rel_path),
            {component["target"]:"opencv::{}".format(component["target"]) for component in self._opencv_components}
        )

    def _create_cmake_module_variables(self, module_file):
        """
        Define several CMake variables from upstream CMake config file not defined by default by CMakeDeps.
        See https://github.com/opencv/opencv/blob/3.4.20/cmake/templates/OpenCVConfig.cmake.in
        """
        v = Version(self.version)
        content = textwrap.dedent(f"""\
            if(NOT DEFINED OpenCV_LIBS)
                set(OpenCV_LIBS opencv::opencv)
            endif()
            if(NOT DEFINED OpenCV_VERSION_MAJOR)
                set(OpenCV_VERSION_MAJOR {v.major})
            endif()
            if(NOT DEFINED OpenCV_VERSION_MINOR)
                set(OpenCV_VERSION_MINOR {v.minor})
            endif()
            if(NOT DEFINED OpenCV_VERSION_PATCH)
                set(OpenCV_VERSION_PATCH {v.patch})
            endif()
        """)
        save(self, module_file, content)

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
    def _module_vars_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    @property
    def _module_target_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    @property
    def _opencv_components(self):
        def imageformats_deps():
            components = []
            if self.options.with_jasper:
                components.append("jasper::jasper")
            if self.options.with_png:
                components.append("libpng::libpng")
            if self.options.with_jpeg == "libjpeg":
                components.append("libjpeg::libjpeg")
            elif self.options.with_jpeg == "libjpeg-turbo":
                components.append("libjpeg-turbo::jpeg")
            elif self.options.with_jpeg == "mozjpeg":
                components.append("mozjpeg::libjpeg")
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
        debug = "d" if self.settings.build_type == "Debug" and is_msvc(self) else ""

        def get_lib_name(module):
            if module in ("correspondence", "multiview", "numeric"):
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
                self.cpp_info.components[conan_component].libs = [lib_name]
                self.cpp_info.components[conan_component].requires = requires
                if self.settings.os in ["Linux", "FreeBSD"]:
                    self.cpp_info.components[conan_component].system_libs = ["dl", "m", "pthread", "rt"]

                # TODO: to remove in conan v2 once cmake_find_package* generators removed
                self.cpp_info.components[conan_component].names["cmake_find_package"] = cmake_target
                self.cpp_info.components[conan_component].names["cmake_find_package_multi"] = cmake_target
                self.cpp_info.components[conan_component].build_modules["cmake_find_package"] = [self._module_vars_rel_path, self._module_target_rel_path]
                self.cpp_info.components[conan_component].build_modules["cmake_find_package_multi"] = [self._module_vars_rel_path, self._module_target_rel_path]
                if cmake_component != cmake_target:
                    conan_component_alias = conan_component + "_alias"
                    self.cpp_info.components[conan_component_alias].names["cmake_find_package"] = cmake_component
                    self.cpp_info.components[conan_component_alias].names["cmake_find_package_multi"] = cmake_component
                    self.cpp_info.components[conan_component_alias].requires = [conan_component]
                    self.cpp_info.components[conan_component_alias].bindirs = []
                    self.cpp_info.components[conan_component_alias].includedirs = []
                    self.cpp_info.components[conan_component_alias].libdirs = []

        self.cpp_info.set_property("cmake_file_name", "OpenCV")
        self.cpp_info.set_property("cmake_build_modules", [self._module_vars_rel_path])

        add_components(self._opencv_components)

        if self.settings.os == "Windows":
            self.cpp_info.components["opencv_imgcodecs"].system_libs = ["comctl32", "gdi32", "ole32", "setupapi", "ws2_32", "vfw32"]
        elif self.settings.os == "Macos":
            self.cpp_info.components["opencv_imgcodecs"].frameworks = ["OpenCL", "Accelerate", "CoreMedia", "CoreVideo", "CoreGraphics", "AVFoundation", "QuartzCore", "Cocoa"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "OpenCV"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCV"
