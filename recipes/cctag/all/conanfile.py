from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.43.0"


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

    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.78.0")
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
            any(getattr(self.options["boost"],
                        "without_{}".format(boost_comp),
                        True) for boost_comp in self._required_boost_components)
        if self.options["boost"].header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration(
                "{0} requires non header-only boost with these components: {1}".format(
                    self.name, ", ".join(self._required_boost_components),
                )
            )

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 14)

        # FIXME: add cuda support
        if self.options.with_cuda:
            raise ConanInvalidConfiguration("CUDA not supported yet")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # Cleanup RPATH if Apple in shared lib of install tree
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)",
                              "")
        # Link to OpenCV targets
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                              "${OpenCV_LIBS}",
                              "opencv_core opencv_videoio opencv_imgproc opencv_imgcodecs")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CCTAG_SERIALIZE"] = self.options.serialize
        cmake.definitions["CCTAG_VISUAL_DEBUG"] = self.options.visual_debug
        cmake.definitions["CCTAG_NO_COUT"] = self.options.no_cout
        cmake.definitions["CCTAG_WITH_CUDA"] = self.options.with_cuda
        cmake.definitions["CCTAG_BUILD_APPS"] = False
        cmake.definitions["CCTAG_CUDA_CC_CURRENT_ONLY"] = False
        cmake.definitions["CCTAG_NVCC_WARNINGS"] = False
        cmake.definitions["CCTAG_EIGEN_NO_ALIGN"] = True
        cmake.definitions["CCTAG_USE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        cmake.definitions["CCTAG_ENABLE_SIMD_AVX2"] = False
        cmake.definitions["CCTAG_BUILD_TESTS"] = False
        cmake.definitions["CCTAG_BUILD_DOC"] = False
        cmake.definitions["CCTAG_NO_THRUST_COPY_IF"] = False
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CCTag")
        self.cpp_info.set_property("cmake_target_name", "CCTag::CCTag")
        suffix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = ["CCTag{}".format(suffix)]
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
