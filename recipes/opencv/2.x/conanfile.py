from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
import os
import textwrap

required_conan_version = ">=1.54.0"


OPENCV_MAIN_MODULES_OPTIONS = (
    "calib3d",
    "contrib",
    "features2d",
    "flann",
    "gpu",
    "highgui",
    "imgproc",
    "legacy",
    "ml",
    "objdetect",
    "photo",
    "stitching",
    "superres",
    "ts",
    "video",
    "videostab",
)

OPENCV_EXTRA_MODULES_OPTIONS = (
    "androidcamera",
    "nonfree",
    "ocl",
    "viz",
)

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
        # global options
        "with_eigen": [True, False],
        "with_tbb": [True, False],
        "world": [True, False],
        # highgui module options
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo", "mozjpeg"],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_jasper": [True, False],
        "with_openexr": [True, False],
        "with_gtk": [True, False],
    }
    options.update({_name: [True, False] for _name in OPENCV_MAIN_MODULES_OPTIONS})
    options.update({_name: [True, False] for _name in OPENCV_EXTRA_MODULES_OPTIONS})

    default_options = {
        "shared": False,
        "fPIC": True,
        # global options
        "with_eigen": True,
        "with_tbb": False,
        "world": False,
        # highgui module options
        "with_jpeg": "libjpeg",
        "with_png": True,
        "with_tiff": True,
        "with_jasper": True,
        "with_openexr": True,
        "with_gtk": True,
    }
    default_options.update({_name: True for _name in OPENCV_MAIN_MODULES_OPTIONS})
    default_options.update({_name: False for _name in OPENCV_EXTRA_MODULES_OPTIONS})

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Android":
            del self.options.androidcamera
        if self.settings.os == "iOS":
            del self.options.gpu
            del self.options.superres
            del self.options.ts
        if self.settings.os != "Linux":
            del self.options.with_gtk

    @property
    def _opencv_modules(self):
        def imageformats_deps():
            components = []
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
            if self.options.get_safe("with_jasper"):
                components.append("jasper::jasper")
            if self.options.get_safe("with_openexr"):
                components.append("openexr::openexr")
            return components

        def eigen():
            return ["eigen::eigen"] if self.options.with_eigen else []

        def gtk():
            return ["gtk::gtk"] if self.options.get_safe("with_gtk") else []

        def tbb():
            return ["onetbb::onetbb"] if self.options.with_tbb else []

        def opencv_gpu():
            return ["opencv_gpu"] if self.options.get_safe("gpu") else []

        def opencv_highgui():
            return ["opencv_highgui"] if self.options.highgui else []

        def opencv_nonfree():
            return ["opencv_nonfree"] if self.options.nonfree else []

        def opencv_ocl():
            return ["opencv_ocl"] if self.options.ocl else []

        def opencv_androidcamera():
            return ["opencv_androidcamera"] if self.options.get_safe("androidcamera") else []

        opencv_modules = {
            # Main modules
            "calib3d": {
                "is_built": self.options.calib3d,
                "mandatory_options": ["features2d", "imgproc"],
                "requires": ["opencv_features2d", "opencv_imgproc"] + eigen() + tbb(),
            },
            "contrib": {
                "is_built": self.options.contrib,
                "mandatory_options": ["calib3d", "features2d", "imgproc", "ml", "objdetect", "video"],
                "requires": ["opencv_calib3d", "opencv_features2d", "opencv_imgproc", "opencv_ml", "opencv_objdetect",
                             "opencv_video"] + opencv_highgui() + opencv_nonfree() + eigen() + tbb(),
            },
            "core": {
                "is_built": True,
                "no_option": True,
                "requires": ["zlib::zlib"] + eigen() + tbb(),
                "system_libs": [
                    (self.settings.os == "Android", ["dl", "m", "log"]),
                    (self.settings.os == "FreeBSD", ["m", "pthread"]),
                    (self.settings.os == "Linux", ["dl", "m", "pthread", "rt"]),
                ],
            },
            "features2d": {
                "is_built": self.options.features2d,
                "mandatory_options": ["flann", "imgproc"],
                "requires": ["opencv_flann", "opencv_imgproc"] + opencv_highgui() + eigen() + tbb(),
            },
            "flann": {
                "is_built": self.options.flann,
                "requires": ["opencv_core"] + eigen() + tbb(),
            },
            "gpu": {
                "is_built": self.options.get_safe("gpu"),
                "mandatory_options": ["calib3d", "imgproc", "legacy", "objdetect", "photo", "video"],
                "requires": ["opencv_calib3d", "opencv_imgproc", "opencv_legacy", "opencv_objdetect", "opencv_photo",
                             "opencv_video"] + eigen() + tbb(),
            },
            "highgui": {
                "is_built": self.options.highgui,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_imgproc"] + opencv_androidcamera() + imageformats_deps() + gtk() + eigen() + tbb(),
                "system_libs": [
                    (self.settings.os == "Windows", ["comctl32", "gdi32", "ole32", "setupapi", "ws2_32", "vfw32"]),
                ],
                "frameworks": [
                    (is_apple_os(self), ["Accelerate", "AVFoundation", "CoreFoundation", "CoreGraphics", "CoreMedia",
                                         "CoreVideo", "Foundation", "QuartzCore"]),
                    (self.settings.os == "iOS", ["UIKit"]),
                    (self.settings.os == "Macos", ["AppKit", "Cocoa"]),
                ],
            },
            "imgproc": {
                "is_built": self.options.imgproc,
                "requires": ["opencv_core"] + eigen() + tbb(),
            },
            "legacy": {
                "is_built": self.options.legacy,
                "mandatory_options": ["calib3d", "ml", "video"],
                "requires": ["opencv_calib3d", "opencv_ml", "opencv_video"] + opencv_highgui() + eigen() + tbb(),
            },
            "ml": {
                "is_built": self.options.ml,
                "requires": ["opencv_core"] + eigen() + tbb(),
            },
            "objdetect": {
                "is_built": self.options.objdetect,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_core", "opencv_imgproc"] + opencv_highgui() + eigen() + tbb(),
            },
            "photo": {
                "is_built": self.options.photo,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_imgproc"] + eigen() + tbb(),
            },
            "stitching": {
                "is_built": self.options.stitching,
                "mandatory_options": ["calib3d", "features2d", "imgproc", "objdetect"],
                "requires": ["opencv_calib3d", "opencv_features2d", "opencv_imgproc", "opencv_objdetect"] +
                            opencv_gpu() + opencv_nonfree() + eigen() + tbb(),
            },
            "superres": {
                "is_built": self.options.get_safe("superres"),
                "mandatory_options": ["imgproc", "video"],
                "requires": ["opencv_imgproc", "opencv_video"] + opencv_gpu() + opencv_highgui() + opencv_ocl() +
                            eigen() + tbb(),
            },
            "ts": {
                "is_built": self.options.get_safe("ts"),
                "is_part_of_world": False,
                "mandatory_options": ["calib3d", "features2d", "highgui", "imgproc", "video"],
                "requires": ["opencv_core", "opencv_calib3d", "opencv_features2d", "opencv_highgui", "opencv_imgproc",
                             "opencv_video"] + eigen() + tbb(),
            },
            "video": {
                "is_built": self.options.video,
                "mandatory_options": ["imgproc"],
                "requires": ["opencv_imgproc"] + eigen() + tbb(),
            },
            "videostab": {
                "is_built": self.options.videostab,
                "mandatory_options": ["calib3d", "features2d", "highgui", "imgproc", "photo", "video"],
                "requires": ["opencv_calib3d", "opencv_features2d", "opencv_highgui", "opencv_imgproc", "opencv_photo",
                             "opencv_video"] + opencv_gpu() + eigen() + tbb(),
            },
            # Extra modules
            "androidcamera": {
                "is_built": self.options.get_safe("androidcamera"),
                "requires": ["opencv_core"] + eigen() + tbb(),
                "system_libs": [
                    (self.settings.os == "Android", ["dl", "log"]),
                ],
            },
            "nonfree": {
                "is_built": self.options.nonfree,
                "mandatory_options": ["calib3d", "features2d", "imgproc"],
                "requires": ["opencv_calib3d", "opencv_features2d", "opencv_imgproc"] + opencv_gpu() + opencv_ocl() +
                            eigen() + tbb(),
            },
            "ocl": {
                "is_built": self.options.ocl,
                "mandatory_options": ["calib3d", "features2d", "imgproc", "ml", "objdetect", "video"],
                "requires": ["opencv_calib3d", "opencv_core", "opencv_features2d", "opencv_imgproc", "opencv_ml",
                             "opencv_objdetect", "opencv_video"] + eigen() + tbb(),
                "frameworks": [
                    (self.settings.os == "Macos", ["OpenCL"]),
                ],
            },
            "viz": {
                "is_built": self.options.viz,
                "requires": ["opencv_core", "vtk::vtk"] + eigen() + tbb(),
            },
        }

        return opencv_modules

    def _get_mandatory_disabled_options(self, opencv_modules):
        direct_options_to_enable = {}
        transitive_options_to_enable = {}

        # Check which direct options have to be enabled
        base_options = [option for option, values in opencv_modules.items()
                        if not values.get("no_option") and self.options.get_safe(option)]
        for base_option in base_options:
            for mandatory_option in opencv_modules.get(base_option, {}).get("mandatory_options", []):
                if not self.options.get_safe(mandatory_option):
                    direct_options_to_enable.setdefault(mandatory_option, set()).add(base_option)

        # Now traverse the graph to check which transitive options have to be enabled
        def collect_transitive_options(base_option, option):
            for mandatory_option in opencv_modules.get(option, {}).get("mandatory_options", []):
                if not self.options.get_safe(mandatory_option):
                    if mandatory_option not in transitive_options_to_enable:
                        transitive_options_to_enable[mandatory_option] = set()
                        collect_transitive_options(base_option, mandatory_option)
                    if base_option not in direct_options_to_enable.get(mandatory_option, set()):
                        transitive_options_to_enable[mandatory_option].add(base_option)

        for base_option in base_options:
            collect_transitive_options(base_option, base_option)

        return {
            "direct": direct_options_to_enable,
            "transitive": transitive_options_to_enable,
        }

    def _solve_internal_dependency_graph(self, opencv_modules):
        disabled_options = self._get_mandatory_disabled_options(opencv_modules)
        direct_options_to_enable = disabled_options["direct"]
        transitive_options_to_enable = disabled_options["transitive"]

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

        # Call this first before any further manipulation of options based on other options
        self._solve_internal_dependency_graph(self._opencv_modules)

        if not self.options.highgui:
            self.options.rm_safe("with_jpeg")
            self.options.rm_safe("with_png")
            self.options.rm_safe("with_tiff")
            self.options.rm_safe("with_jasper")
            self.options.rm_safe("with_openexr")
            self.options.rm_safe("with_gtk")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/1.2.13")
        if self.options.with_eigen:
            self.requires("eigen/3.4.0")
        if self.options.with_tbb:
            # opencv 2.x doesn't support onetbb >= 2021
            self.requires("onetbb/2020.3")
        # highgui module options
        if self.options.get_safe("with_jpeg") == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.get_safe("with_jpeg") == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.4")
        elif self.options.get_safe("with_jpeg") == "mozjpeg":
            self.requires("mozjpeg/4.1.1")
        if self.options.get_safe("with_png"):
            self.requires("libpng/1.6.39")
        if self.options.get_safe("with_jasper"):
            self.requires("jasper/4.0.0")
        if self.options.get_safe("with_openexr"):
            # opencv 2.x doesn't support openexr >= 3
            self.requires("openexr/2.5.7")
        if self.options.get_safe("with_tiff"):
            self.requires("libtiff/4.4.0")
        if self.options.get_safe("with_gtk"):
            self.requires("gtk/system")

    def _check_mandatory_options(self, opencv_modules):
        disabled_options = self._get_mandatory_disabled_options(opencv_modules)
        direct_disabled_mandatory_options = disabled_options["direct"]
        transitive_disabled_mandatory_options = disabled_options["transitive"]

        # check mandatory options
        all_disabled_mandatory_options = set(direct_disabled_mandatory_options.keys())
        all_disabled_mandatory_options.update(transitive_disabled_mandatory_options.keys())
        if all_disabled_mandatory_options:
            message = ("Several opencv options are disabled but are required by modules "
                       "you have explicitly requested:\n")

            for disabled_option in all_disabled_mandatory_options:
                direct_and_transitive = []
                direct = ", ".join(direct_disabled_mandatory_options.get(disabled_option, []))
                if direct:
                    direct_and_transitive.append(f"direct dependency of {direct}")
                transitive = ", ".join(transitive_disabled_mandatory_options.get(disabled_option, []))
                if transitive:
                    direct_and_transitive.append(f"transitive dependency of {transitive}")
                message += f"  - {disabled_option}: {' / '.join(direct_and_transitive)}\n"

            raise ConanInvalidConfiguration(message)

    def validate(self):
        self._check_mandatory_options(self._opencv_modules)
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Visual Studio with static runtime is not supported for shared library.")
        if self.options.viz:
            raise ConanInvalidConfiguration(
                "viz module can't be enabled yet. It requires VTK which is not available in conan-center."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)
        rmdir(self, os.path.join(self.source_folder, "3rdparty"))

        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")

        for cascade in ["lbpcascades", "haarcascades"]:
            replace_in_file(self, os.path.join(self.source_folder, "data", "CMakeLists.txt"),
                                  f"share/OpenCV/{cascade}", f"res/{cascade}")

        replace_in_file(self, cmakelists, "staticlib", "lib")
        replace_in_file(self, cmakelists, "ANDROID OR NOT UNIX", "FALSE")
        replace_in_file(self, cmakelists, "${OpenCV_ARCH}/${OpenCV_RUNTIME}/", "")
        replace_in_file(self, os.path.join(self.source_folder, "modules", "highgui", "CMakeLists.txt"), "JASPER_", "Jasper_")

        # relocatable shared lib on macOS
        replace_in_file(self, cmakelists, "cmake_policy(SET CMP0042 OLD)", "cmake_policy(SET CMP0042 NEW)")
        # Cleanup RPATH
        replace_in_file(self, cmakelists,
                              "set(CMAKE_INSTALL_RPATH \"${CMAKE_INSTALL_PREFIX}/${OPENCV_LIB_INSTALL_PATH}\")",
                              "")
        replace_in_file(self, cmakelists, "set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)", "")

        # Do not try to detect Python
        replace_in_file(self, cmakelists, "include(cmake/OpenCVDetectPython.cmake)", "")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_ANDROID_EXAMPLES"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_DOCS"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_PACKAGE"] = False
        tc.variables["BUILD_PERF_TESTS"] = False
        tc.variables["BUILD_opencv_apps"] = False
        tc.variables["BUILD_opencv_java"] = False
        tc.variables["BUILD_ZLIB"] = False
        tc.variables["BUILD_JPEG"] = False
        tc.variables["BUILD_PNG"] = False
        tc.variables["BUILD_TIFF"] = False
        tc.variables["BUILD_JASPER"] = False
        tc.variables["BUILD_OPENEXR"] = False
        tc.variables["BUILD_TBB"] = False
        tc.variables["WITH_VTK"] = self.options.viz
        tc.variables["WITH_CUFFT"] = False
        tc.variables["WITH_CUBLAS"] = False
        tc.variables["WITH_NVCUVID"] = False
        tc.variables["WITH_FFMPEG"] = False
        tc.variables["WITH_GSTREAMER"] = False
        tc.variables["WITH_OPENCL"] = self.options.ocl
        tc.variables["WITH_CUDA"] = False
        tc.variables["WITH_GTK"] = self.options.get_safe("with_gtk", False)
        tc.variables["WITH_JPEG"] = bool(self.options.get_safe("with_jpeg", False))
        tc.variables["WITH_PNG"] = self.options.get_safe("with_png", False)
        tc.variables["WITH_TIFF"] = self.options.get_safe("with_tiff", False)
        tc.variables["WITH_JASPER"] = self.options.get_safe("with_jasper", False)
        tc.variables["WITH_OPENEXR"] = self.options.get_safe("with_openexr", False)
        if self.options.get_safe("with_openexr") and not valid_min_cppstd(self, 11):
            tc.variables["CMAKE_CXX_STANDARD"] = 11
        tc.variables["WITH_EIGEN"] = self.options.with_eigen
        tc.variables["WITH_QT"] = False
        tc.variables["WITH_TBB"] = self.options.with_tbb
        tc.variables["WITH_OPENMP"] = False
        tc.variables["OPENCV_MODULES_PUBLIC"] = "opencv"
        # Main modules
        tc.variables["BUILD_opencv_calib3d"] = self.options.calib3d
        tc.variables["BUILD_opencv_contrib"] = self.options.contrib
        tc.variables["BUILD_opencv_core"] = True
        tc.variables["BUILD_opencv_features2d"] = self.options.features2d
        tc.variables["BUILD_opencv_flann"] = self.options.flann
        tc.variables["BUILD_opencv_gpu"] = self.options.get_safe("gpu", False)
        tc.variables["BUILD_opencv_highgui"] = self.options.highgui
        tc.variables["BUILD_opencv_imgproc"] = self.options.imgproc
        tc.variables["BUILD_opencv_legacy"] = self.options.legacy
        tc.variables["BUILD_opencv_ml"] = self.options.ml
        tc.variables["BUILD_opencv_objdetect"] = self.options.objdetect
        tc.variables["BUILD_opencv_photo"] = self.options.photo
        tc.variables["BUILD_opencv_stitching"] = self.options.stitching
        tc.variables["BUILD_opencv_superres"] = self.options.get_safe("superres", False)
        tc.variables["BUILD_opencv_ts"] = self.options.get_safe("ts", False)
        tc.variables["BUILD_opencv_video"] = self.options.video
        tc.variables["BUILD_opencv_videostab"] = self.options.videostab
        tc.variables["BUILD_opencv_world"] = self.options.world
        # Extra modules
        tc.variables["BUILD_opencv_androidcamera"] = self.options.get_safe("androidcamera", False)
        tc.variables["BUILD_opencv_dynamicuda"] = False
        tc.variables["BUILD_opencv_nonfree"] = self.options.nonfree
        tc.variables["BUILD_opencv_ocl"] = self.options.ocl
        tc.variables["BUILD_opencv_viz"] = self.options.viz

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
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "staticlib"))
        rm(self, "*.cmake", self.package_folder, recursive=True)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        targets_mapping = {self._cmake_target(k): f"opencv::{self._cmake_target(k)}" for k in self._opencv_modules.keys()}
        if self.options.world:
            targets_mapping.update({"opencv_world": "opencv::opencv_world"})
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            targets_mapping,
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

    @staticmethod
    def _cmake_target(module):
        return f"opencv_{module}"

    def package_info(self):
        version = self.version.split(".")[:-1]  # last version number is not used
        version = "".join(version) if self.settings.os == "Windows" else ""
        debug = "d" if self.settings.build_type == "Debug" and is_msvc(self) else ""

        def get_lib_name(module):
            return f"opencv_{module}{version}{debug}"

        def add_components(components):
            if self.options.world:
                self.cpp_info.components["opencv_world"].set_property("cmake_target_name", "opencv_world")
                self.cpp_info.components["opencv_world"].libs = [get_lib_name("world")]
                world_requires = set()
                world_requires_exclude = set()
                world_system_libs = set()
                world_frameworks = set()

            for module, values in components.items():
                if not values.get("is_built"):
                    continue
                cmake_target = self._cmake_target(module)
                conan_component = cmake_target
                # TODO: we should also define COMPONENTS names of each target for find_package() but not possible yet in CMakeDeps
                #       see https://github.com/conan-io/conan/issues/10258
                self.cpp_info.components[conan_component].set_property("cmake_target_name", cmake_target)

                module_requires = values.get("requires", [])
                module_system_libs = []
                for _condition, _system_libs in values.get("system_libs", []):
                    if _condition:
                        module_system_libs.extend(_system_libs)
                module_frameworks = []
                for _condition, _frameworks in values.get("frameworks", []):
                    if _condition:
                        module_frameworks.extend(_frameworks)

                if self.options.world and values.get("is_part_of_world", True):
                    self.cpp_info.components[conan_component].requires = ["opencv_world"]
                    world_requires.update(module_requires)
                    world_requires_exclude.add(conan_component)
                    world_system_libs.update(module_system_libs)
                    world_frameworks.update(module_frameworks)
                else:
                    self.cpp_info.components[conan_component].libs = [get_lib_name(module)]
                    self.cpp_info.components[conan_component].requires = module_requires
                    self.cpp_info.components[conan_component].system_libs = module_system_libs
                    self.cpp_info.components[conan_component].frameworks = module_frameworks

                # TODO: to remove in conan v2 once cmake_find_package* generators removed
                self.cpp_info.components[conan_component].names["cmake_find_package"] = cmake_target
                self.cpp_info.components[conan_component].names["cmake_find_package_multi"] = cmake_target
                self.cpp_info.components[conan_component].build_modules["cmake_find_package"] = [self._module_file_rel_path]
                self.cpp_info.components[conan_component].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
                if module != cmake_target:
                    conan_component_alias = conan_component + "_alias"
                    self.cpp_info.components[conan_component_alias].names["cmake_find_package"] = module
                    self.cpp_info.components[conan_component_alias].names["cmake_find_package_multi"] = module
                    self.cpp_info.components[conan_component_alias].requires = [conan_component]
                    self.cpp_info.components[conan_component_alias].bindirs = []
                    self.cpp_info.components[conan_component_alias].includedirs = []
                    self.cpp_info.components[conan_component_alias].libdirs = []

            if self.options.world:
                self.cpp_info.components["opencv_world"].requires = list(world_requires - world_requires_exclude)
                self.cpp_info.components["opencv_world"].system_libs = list(world_system_libs)
                self.cpp_info.components["opencv_world"].frameworks = list(world_frameworks)

                # TODO: to remove in conan v2 once cmake_find_package* generators removed
                self.cpp_info.components["opencv_world"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
                self.cpp_info.components["opencv_world"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

        self.cpp_info.set_property("cmake_file_name", "OpenCV")

        add_components(self._opencv_modules)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "OpenCV"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenCV"
