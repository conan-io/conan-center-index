from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
from conans import CMake
import os
import textwrap

required_conan_version = ">=1.53.0"


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
        "with_jpeg": [True, False],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_jasper": [True, False],
        "with_openexr": [True, False],
        "with_eigen": [True, False],
        "with_tbb": [True, False],
        "with_gtk": [True, False],
        "nonfree": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jpeg": True,
        "with_png": True,
        "with_tiff": True,
        "with_jasper": True,
        "with_openexr": True,
        "with_eigen": True,
        "with_tbb": False,
        "with_gtk": True,
        "nonfree": False,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_folder(self):
        return os.path.join(self.source_folder, "src")

    @property
    def _build_folder(self):
        return os.path.join(self.source_folder, "build")

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_gtk

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        pass

    def requirements(self):
        self.requires("zlib/1.2.13")
        if self.options.with_jpeg:
            self.requires("libjpeg/9e")
        if self.options.with_png:
            self.requires("libpng/1.6.39")
        if self.options.with_jasper:
            self.requires("jasper/2.0.33")
        if self.options.with_openexr:
            self.requires("openexr/2.5.7")
        if self.options.with_tiff:
            self.requires("libtiff/4.4.0")
        if self.options.with_eigen:
            self.requires("eigen/3.4.0")
        if self.options.with_tbb:
            # opencv 2.x doesn't support onetbb >= 2021
            self.requires("onetbb/2020.3")
        if self.options.get_safe("with_gtk"):
            self.requires("gtk/system")

    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio with static runtime is not supported for shared library.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self._source_folder, strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)
        rmdir(self, os.path.join(self._source_folder, "3rdparty"))

        cmakelists = os.path.join(self._source_folder, "CMakeLists.txt")

        # allow to find conan-supplied OpenEXR
        if self.options.with_openexr:
            find_openexr = os.path.join(self._source_folder, "cmake", "OpenCVFindOpenEXR.cmake")
            replace_in_file(self, find_openexr,
                                  r'SET(OPENEXR_ROOT "C:/Deploy" CACHE STRING "Path to the OpenEXR \"Deploy\" folder")',
                                  "")
            replace_in_file(self, find_openexr, r'set(OPENEXR_ROOT "")', "")
            replace_in_file(self, find_openexr, "SET(OPENEXR_LIBSEARCH_SUFFIXES x64/Release x64 x64/Debug)", "")
            replace_in_file(self, find_openexr, "SET(OPENEXR_LIBSEARCH_SUFFIXES Win32/Release Win32 Win32/Debug)", "")

            def openexr_library_names(name):
                # OpenEXR library may have different names, depends on namespace versioning, static, debug, etc.
                openexr_version = Version(self.dependencies["openexr"].ref.version)
                suffix = f"{openexr_version.major}_{openexr_version.minor}"
                names = [
                    f"{name}-{suffix}",
                    f"{name}-{suffix}_s",
                    f"{name}-{suffix}_d",
                    f"{name}-{suffix}_s_d",
                    name,
                    f"{name}_s",
                    f"{name}_d",
                    f"{name}_s_d",
                ]
                return " ".join(names)

            for lib in ["Half", "Iex", "Imath", "IlmImf", "IlmThread"]:
                replace_in_file(self, find_openexr, f"NAMES {lib}", f"NAMES {openexr_library_names(lib)}")

            replace_in_file(self, cmakelists,
                                "project(OpenCV CXX C)", "project(OpenCV CXX C)\nset(CMAKE_CXX_STANDARD 11)")

        for cascade in ["lbpcascades", "haarcascades"]:
            replace_in_file(self, os.path.join(self._source_folder, "data", "CMakeLists.txt"),
                                  f"share/OpenCV/{cascade}", f"res/{cascade}")

        replace_in_file(self, cmakelists, "staticlib", "lib")
        replace_in_file(self, cmakelists, "ANDROID OR NOT UNIX", "FALSE")
        replace_in_file(self, cmakelists, "${OpenCV_ARCH}/${OpenCV_RUNTIME}/", "")
        replace_in_file(self, os.path.join(self._source_folder, "modules", "highgui", "CMakeLists.txt"), "JASPER_", "Jasper_")

        # relocatable shared lib on macOS
        replace_in_file(self, cmakelists, "cmake_policy(SET CMP0042 OLD)", "cmake_policy(SET CMP0042 NEW)")
        # Cleanup RPATH
        replace_in_file(self, cmakelists,
                              "set(CMAKE_INSTALL_RPATH \"${CMAKE_INSTALL_PREFIX}/${OPENCV_LIB_INSTALL_PATH}\")",
                              "")
        replace_in_file(self, cmakelists, "set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)", "")

        # Do not try to detect Python
        replace_in_file(self, cmakelists, "include(cmake/OpenCVDetectPython.cmake)", "")

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

        self._cmake.definitions["WITH_GTK"] = self.options.get_safe("with_gtk", False)
        self._cmake.definitions["WITH_JPEG"] = self.options.with_jpeg
        self._cmake.definitions["WITH_PNG"] = self.options.with_png
        self._cmake.definitions["WITH_TIFF"] = self.options.with_tiff
        self._cmake.definitions["WITH_JASPER"] = self.options.with_jasper
        self._cmake.definitions["WITH_OPENEXR"] = self.options.with_openexr
        self._cmake.definitions["WITH_EIGEN"] = self.options.with_eigen
        self._cmake.definitions["WITH_TBB"] = self.options.with_tbb
        self._cmake.definitions["OPENCV_MODULES_PUBLIC"] = "opencv"
        self._cmake.definitions["BUILD_opencv_nonfree"] = self.options.nonfree

        self._cmake.definitions["ENABLE_CCACHE"] = False

        if is_msvc(self):
            self._cmake.definitions["BUILD_WITH_STATIC_CRT"] = is_msvc_static_runtime(self)
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
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "staticlib"))
        rm(self, "*.cmake", self.package_folder, recursive=True)

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

    @property
    def _opencv_components(self):
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
            return ["onetbb::onetbb"] if self.options.with_tbb else []

        def gtk():
            return ["gtk::gtk"] if self.options.get_safe("with_gtk") else []

        def nonfree():
            return ["opencv_nonfree"] if self.options.nonfree else []

        opencv_components = [
            {"target": "opencv_core",       "lib": "core",       "requires": ["zlib::zlib"] + tbb()},
            {"target": "opencv_flann",      "lib": "flann",      "requires": ["opencv_core"] + tbb()},
            {"target": "opencv_imgproc",    "lib": "imgproc",    "requires": ["opencv_core"] + tbb()},
            {"target": "opencv_highgui",    "lib": "highgui",    "requires": ["opencv_core", "opencv_imgproc"] + eigen() + tbb() + gtk() + imageformats_deps()},
            {"target": "opencv_features2d", "lib": "features2d", "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui"] + tbb()},
            {"target": "opencv_calib3d",    "lib": "calib3d",    "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d"] + tbb()},
            {"target": "opencv_ml",         "lib": "ml",         "requires": ["opencv_core"] + tbb()},
            {"target": "opencv_video",      "lib": "video",      "requires": ["opencv_core", "opencv_imgproc"] + tbb()},
            {"target": "opencv_legacy",     "lib": "legacy",     "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_ml", "opencv_video"] + eigen() + tbb()},
            {"target": "opencv_objdetect",  "lib": "objdetect",  "requires": ["opencv_core", "opencv_imgproc", "opencv_highgui"] + tbb()},
            {"target": "opencv_photo",      "lib": "photo",      "requires": ["opencv_core", "opencv_imgproc"] + tbb()},
            {"target": "opencv_gpu",        "lib": "gpu",        "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_ml", "opencv_video", "opencv_legacy", "opencv_objdetect", "opencv_photo"] + tbb()},
            {"target": "opencv_contrib",    "lib": "contrib",    "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_ml", "opencv_video", "opencv_legacy", "opencv_objdetect", "opencv_photo", "opencv_gpu"] + nonfree() + tbb()},
            {"target": "opencv_stitching",  "lib": "stitching",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_ml", "opencv_video", "opencv_legacy", "opencv_objdetect", "opencv_photo", "opencv_gpu"] + nonfree() + tbb()},
            {"target": "opencv_superres",   "lib": "superres",   "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_ml", "opencv_video", "opencv_legacy", "opencv_objdetect", "opencv_photo", "opencv_gpu"] + tbb()},
            {"target": "opencv_ts",         "lib": "ts",         "requires": ["opencv_core", "opencv_flann", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_video"] + tbb()},
            {"target": "opencv_videostab",  "lib": "videostab",  "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_ml", "opencv_video", "opencv_legacy", "opencv_objdetect", "opencv_photo", "opencv_gpu"] + tbb()}
        ]
        if self.options.nonfree:
            opencv_components.append({"target": "opencv_nonfree", "lib": "nonfree", "requires": ["opencv_core", "opencv_flann", "opencv_imgproc", "opencv_highgui", "opencv_features2d", "opencv_calib3d", "opencv_ml", "opencv_video", "opencv_legacy", "opencv_objdetect", "opencv_photo", "opencv_gpu"] + tbb()})

        return opencv_components

    def package_info(self):
        version = self.version.split(".")[:-1]  # last version number is not used
        version = "".join(version) if self.settings.os == "Windows" else ""
        debug = "d" if self.settings.build_type == "Debug" and is_msvc(self) else ""

        def get_lib_name(module):
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
                self.cpp_info.components[conan_component].requires = requires
                if self.settings.os in ["Linux", "FreeBSD"]:
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
                    self.cpp_info.components[conan_component_alias].bindirs = []
                    self.cpp_info.components[conan_component_alias].includedirs = []
                    self.cpp_info.components[conan_component_alias].libdirs = []

        self.cpp_info.set_property("cmake_file_name", "OpenCV")

        add_components(self._opencv_components)

        if self.settings.os == "Windows":
            self.cpp_info.components["opencv_highgui"].system_libs = ["comctl32", "gdi32", "ole32", "setupapi", "ws2_32", "vfw32"]
        elif self.settings.os == "Macos":
            self.cpp_info.components["opencv_highgui"].frameworks = ["Cocoa"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "OpenCV"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCV"
