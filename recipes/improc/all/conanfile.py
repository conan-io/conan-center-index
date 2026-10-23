from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
import os


class ImprocConan(ConanFile):
    name = "improc"
    description = (
        "Type-safe C++23 image processing library built on OpenCV. "
        "Provides a composable pipeline API, geometric/filter/morphological ops, "
        "camera I/O, ML model loaders, camera calibration, and optional ONNX Runtime inference."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/michalmaj/improc"
    topics = ("image-processing", "opencv", "computer-vision", "cpp23", "pipeline")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared":    [True, False],
        "fPIC":      [True, False],
        "with_onnx": [True, False],
    }
    default_options = {
        "shared":    False,
        "fPIC":      True,
        "with_onnx": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.with_onnx:
            # onnxruntime bundles its own protobuf; enabling OpenCV's protobuf causes
            # duplicate symbol errors at link time.
            self.options["opencv"].with_protobuf = False
            # onnxruntime requires Eigen >= 5.x; OpenCV defaults to bundled 3.4.x,
            # which produces a Conan graph conflict. Disabling opencv's bundled Eigen
            # lets the explicit eigen/5.x requirement in requirements() win.
            try:
                self.options["opencv"].with_eigen = False
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder=".")

    def validate(self):
        check_min_cppstd(self, "23")

        compiler = str(self.settings.compiler)
        version = Version(str(self.settings.compiler.version))

        if compiler == "gcc" and version < "14":
            raise ConanInvalidConfiguration("improc requires GCC >= 14 for full C++23 support")
        if compiler == "clang" and version < "18":
            raise ConanInvalidConfiguration("improc requires Clang >= 18 for full C++23 support")
        if compiler == "apple-clang" and version < "16":
            raise ConanInvalidConfiguration(
                "improc requires Apple-Clang >= 16 (Xcode 16); "
                "older Apple-Clang versions are not validated for this C++23 codebase"
            )
        if compiler == "msvc":
            raise ConanInvalidConfiguration(
                "improc C++23 support with MSVC is not validated in this recipe"
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.30 <4]")

    def requirements(self):
        self.requires("opencv/4.10.0")
        # nlohmann_json is used unconditionally by the COCO dataset loader (src/ml/coco_dataset.cpp).
        # visible=False: it is a private impl dep — not exposed in improc's public headers.
        self.requires("nlohmann_json/3.11.3", visible=False)
        if self.options.with_onnx:
            self.requires("onnxruntime/1.24.4")
            # Force Eigen >= 5.0.1 to satisfy onnxruntime; opencv defaults to 3.4.0
            self.requires("eigen/5.0.1", override=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"]               = self.options.shared
        tc.variables["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        tc.variables["IMPROC_WITH_ONNX"]                = self.options.with_onnx
        tc.variables["IMPROC_BUILD_TESTS"]              = False
        tc.variables["IMPROC_BUILD_EXAMPLES"]           = False
        tc.variables["IMPROC_WITH_DEPTHAI"]             = False
        tc.variables["IMPROC_BENCHMARKS"]               = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # Remove the upstream cmake config — Conan generates its own cmake integration
        # from package_info(). The installed improcConfig.cmake calls find_dependency(OpenCV)
        # which doesn't resolve correctly in Conan consumers' cmake context.
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "improc")
        self.cpp_info.set_property("cmake_target_name", "improc::improc")
        self.cpp_info.libs = ["improc"]

        # Conan 2's CMakeDeps generates empty INTERFACE_INCLUDE_DIRECTORIES for
        # transitive package components.  Because improc's installed public headers
        # include <opencv2/…> directly, consumers cannot compile against them unless
        # we expose opencv's include paths through our own cpp_info.includedirs.
        opencv_pkg = self.dependencies["opencv"]
        opencv_root = opencv_pkg.package_folder
        seen = set()
        for comp in opencv_pkg.cpp_info.components.values():
            for rel_inc in comp.includedirs:
                abs_inc = os.path.join(opencv_root, rel_inc)
                if abs_inc not in seen:
                    seen.add(abs_inc)
                    self.cpp_info.includedirs.append(abs_inc)

        # Link to the specific opencv modules whose headers appear in improc's
        # installed public API.
        self.cpp_info.requires = [
            "opencv::opencv_core",
            "opencv::opencv_imgproc",
            "opencv::opencv_highgui",
            "opencv::opencv_imgcodecs",
            "opencv::opencv_videoio",
            "opencv::opencv_dnn",
            "opencv::opencv_objdetect",
            "opencv::opencv_calib3d",
            "opencv::opencv_features2d",
            "opencv::opencv_photo",
            "opencv::opencv_stitching",
            "opencv::opencv_video",
        ]
        if self.options.with_onnx:
            self.cpp_info.defines = ["IMPROC_WITH_ONNX"]
            self.cpp_info.requires.append("onnxruntime::onnxruntime")
            # When onnxruntime is present it also depends on nlohmann_json, making it
            # visible in the resolved graph. Conan 2's package_info() validator then
            # requires it to be listed here. Without onnxruntime the visible=False dep
            # stays quiet and must NOT appear in cpp_info.requires (shared-lib builds
            # fail with "not a direct requirement" if it does).
            self.cpp_info.requires.append("nlohmann_json::nlohmann_json")
