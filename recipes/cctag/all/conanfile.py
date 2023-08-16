from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc_static_runtime
import os

required_conan_version = ">=1.53.0"


class CCTagConan(ConanFile):
    name = "cctag"
    description = "Detection of CCTag markers made up of concentric circles."
    license = "MPL-2.0"
    topics = ("cctag", "computer-vision", "detection", "image-processing",
              "markers", "fiducial-markers", "concentric-circles")
    homepage = "https://github.com/alicevision/CCTag"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "serialize": [True, False],
        "visual_debug": [True, False],
        "no_cout": [True, False],
        "with_cuda": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "serialize": False,
        "visual_debug": False,
        "no_cout": True,
        "with_cuda": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.80.0")
        self.requires("eigen/3.4.0")
        self.requires("onetbb/2020.3")
        self.requires("opencv/4.5.5")

    @property
    def _required_boost_components(self):
        return [
            "atomic", "chrono", "date_time", "exception", "filesystem",
            "math", "serialization", "stacktrace", "system", "thread", "timer",
        ]

    def validate(self):
        miss_boost_required_comp = \
            any(getattr(self.dependencies["boost"].options,
                        f"without_{boost_comp}",
                        True) for boost_comp in self._required_boost_components)
        if self.dependencies["boost"].options.header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires non header-only boost with these components: "
                f"{', '.join(self._required_boost_components)}",
            )

        if self.settings.compiler == "Visual Studio" and not self.options.shared and \
           is_msvc_static_runtime(self) and self.dependencies["onetbb"].options.shared:
            raise ConanInvalidConfiguration("this specific configuration is prevented due to internal c3i limitations")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)

        # FIXME: add cuda support
        if self.options.with_cuda:
            raise ConanInvalidConfiguration("CUDA not supported yet")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CCTAG_SERIALIZE"] = self.options.serialize
        tc.variables["CCTAG_VISUAL_DEBUG"] = self.options.visual_debug
        tc.variables["CCTAG_NO_COUT"] = self.options.no_cout
        tc.variables["CCTAG_WITH_CUDA"] = self.options.with_cuda
        tc.variables["CCTAG_BUILD_APPS"] = False
        tc.variables["CCTAG_CUDA_CC_CURRENT_ONLY"] = False
        tc.variables["CCTAG_NVCC_WARNINGS"] = False
        tc.variables["CCTAG_EIGEN_NO_ALIGN"] = True
        tc.variables["CCTAG_USE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        tc.variables["CCTAG_ENABLE_SIMD_AVX2"] = False
        tc.variables["CCTAG_BUILD_TESTS"] = False
        tc.variables["CCTAG_BUILD_DOC"] = False
        tc.variables["CCTAG_NO_THRUST_COPY_IF"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Cleanup RPATH if Apple in shared lib of install tree
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                              "SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)",
                              "")
        # Link to OpenCV targets
        replace_in_file(self, os.path.join(self.source_folder, "src", "CMakeLists.txt"),
                              "${OpenCV_LIBS}",
                              "opencv_core opencv_videoio opencv_imgproc opencv_imgcodecs")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CCTag")
        self.cpp_info.set_property("cmake_target_name", "CCTag::CCTag")
        suffix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"CCTag{suffix}"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread"])
        self.cpp_info.requires = [
            "boost::atomic", "boost::chrono", "boost::date_time", "boost::exception",
            "boost::filesystem", "boost::serialization", "boost::system",
            "boost::thread", "boost::timer", "boost::math_c99", "eigen::eigen",
            "onetbb::onetbb", "opencv::opencv_core", "opencv::opencv_videoio",
            "opencv::opencv_imgproc", "opencv::opencv_imgcodecs",
        ]
        if self.settings.os == "Windows":
            self.cpp_info.requires.append("boost::stacktrace_windbg")
        else:
            self.cpp_info.requires.append("boost::stacktrace_basic")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "CCTag"
        self.cpp_info.names["cmake_find_package_multi"] = "CCTag"
