import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class StellaVslamConan(ConanFile):
    name = "stella_vslam"
    description = "stella_vslam is a monocular, stereo, and RGBD visual SLAM system."
    license = "BSD-2-Clause AND BSD-3-Clause AND MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/project/package"
    topics = ("visual-slam", "computer-vision")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_gtsam": [True, False],
        "build_iridescence_viewer": [True, False],
        "build_pangolin_viewer": [True, False],
        "build_socket_viewer": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_iridescence_viewer": False,
        "build_pangolin_viewer": False,
        "build_socket_viewer": False,
        "with_gtsam": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
        }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["g2o"].build_sba_types = True
        self.options["g2o"].build_sim3_types = True
        self.options["g2o"].with_csparse = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True, transitive_libs=True)
        self.requires("g2o/20230806", transitive_headers=True, transitive_libs=True)
        self.requires("llvm-openmp/17.0.6")
        self.requires("nlohmann_json/3.11.3", transitive_headers=True, transitive_libs=True)
        self.requires("opencv/4.9.0", transitive_headers=True, transitive_libs=True)
        self.requires("spdlog/1.14.1", transitive_headers=True, transitive_libs=True)
        self.requires("sqlite3/3.45.3", transitive_headers=True, transitive_libs=True)
        self.requires("stella-cv-fbow/cci.20240107", transitive_headers=True, transitive_libs=True)
        self.requires("tinycolormap/cci.20230223", transitive_headers=True, transitive_libs=True)
        self.requires("yaml-cpp/0.8.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_gtsam:
            self.requires("gtsam/4.2", transitive_headers=True, transitive_libs=True)

        # TODO: add support for viewers
        if self.options.build_iridescence_viewer:
            self.requires("iridescence/cci.20240407")
        if self.options.build_pangolin_viewer:
            self.requires("pangolin/0.9.1")
        if self.options.build_socket_viewer:
            self.requires("protobuf/3.21.12")
            # TODO: add socket.io-client-cpp to CCI
            self.requires("socket.io-client-cpp/3.1.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.options.build_iridescence_viewer:
            raise ConanInvalidConfiguration("build_iridescence_viewer option is not yet implemented")
        if self.options.build_pangolin_viewer:
            raise ConanInvalidConfiguration("build_pangolin_viewer option is not yet implemented")
        if self.options.build_socket_viewer:
            raise ConanInvalidConfiguration("build_socket_viewer option is not yet implemented")

        g2o = self.dependencies["g2o"].options
        if not (g2o.build_sba_types and g2o.build_sim3_types and g2o.with_csparse):
            raise ConanInvalidConfiguration(
                "g2o must be built with g2o/*:build_sba_types=True, "
                "g2o/*:build_sim3_types=True and g2o/*:with_csparse options=True"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["stella_vslam"], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_PROJECT_stella_vslam_INCLUDE"] = "conan_deps.cmake"
        tc.variables["USE_ARUCO"] = self.dependencies["opencv"].options.aruco
        tc.variables["USE_GTSAM"] = self.options.with_gtsam
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        # The project unnecessarily tries to find and link SuiteSparse as a transitive dep for g2o
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_SuiteSparse"] = True
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        rmdir(self, os.path.join(self.source_folder, "3rd"))
        # Latest g2o requires C++17 or newer. Let Conan set the C++ standard.
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "set(CMAKE_CXX_STANDARD 11)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "stella_vslam")
        self.cpp_info.set_property("cmake_target_name", "stella_vslam::stella_vslam")

        self.cpp_info.libs = ["stella_vslam"]

        self.cpp_info.requires = [
            "eigen::eigen",
            "g2o::g2o",
            "llvm-openmp::llvm-openmp",
            "nlohmann_json::nlohmann_json",
            "opencv::opencv_calib3d",
            "opencv::opencv_core",
            "opencv::opencv_features2d",
            "opencv::opencv_imgproc",
            "opencv::opencv_objdetect",
            "spdlog::spdlog",
            "sqlite3::sqlite3",
            "stella-cv-fbow::stella-cv-fbow",
            "tinycolormap::tinycolormap",
            "yaml-cpp::yaml-cpp",
        ]
        if self.options.with_gtsam:
            self.cpp_info.requires.append("gtsam::libgtsam")
        if self.dependencies["opencv"].options.aruco:
            self.cpp_info.requires.append("opencv::opencv_aruco")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
