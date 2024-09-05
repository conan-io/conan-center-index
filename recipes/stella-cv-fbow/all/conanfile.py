import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir, replace_in_file

required_conan_version = ">=1.53.0"


class StellaCvFbowConan(ConanFile):
    name = "stella-cv-fbow"
    description = "FBoW (Fast Bag of Words) is an extremely optimized version of the DBoW2/DBoW3 libraries."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/stella-cv/FBoW"
    topics = ("bag-of-words", "computer-vision", "visual-slam", "dbow")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fast_math": [True, False],
        "avx": [True, False],
        "mmx": [True, False],
        "sse": [True, False],
        "sse2": [True, False],
        "sse3": [True, False],
        "sse4": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "fast_math": True,
        "avx": True,
        "mmx": True,
        "sse": True,
        "sse2": True,
        "sse3": True,
        "sse4": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"] or self.settings.compiler not in ["gcc", "clang", "apple-clang"]:
            del self.options.avx
            del self.options.mmx
            del self.options.sse
            del self.options.sse2
            del self.options.sse3
            del self.options.sse4

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # https://github.com/stella-cv/FBoW/blob/master/include/fbow/vocabulary.h#L35
        self.requires("opencv/4.9.0", transitive_headers=True, transitive_libs=True)
        self.requires("llvm-openmp/17.0.6")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_FAST_MATH"] = self.options.fast_math
        tc.variables["USE_AVX"] = self.options.get_safe("avx", False)
        tc.variables["USE_MMX"] = self.options.get_safe("mmx", False)
        tc.variables["USE_SSE"] = self.options.get_safe("sse", False)
        tc.variables["USE_SSE2"] = self.options.get_safe("sse2", False)
        tc.variables["USE_SSE3"] = self.options.get_safe("sse3", False)
        tc.variables["USE_SSE4"] = self.options.get_safe("sse4", False)
        tc.variables["BUILD_UTILS"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["USE_CONTRIB"] = self.dependencies["opencv"].options.xfeatures2d
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        # Let Conan set the C++ standard
        if self.settings.compiler.cppstd:
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
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fbow")
        self.cpp_info.set_property("cmake_target_name", "fbow::fbow")
        # unofficial
        self.cpp_info.set_property("pkg_config_name", "fbow")

        self.cpp_info.libs = ["fbow"]
        self.cpp_info.requires = [
            "opencv::opencv_core",
            "opencv::opencv_features2d",
            "opencv::opencv_highgui",
            "llvm-openmp::llvm-openmp",
        ]
        if self.dependencies["opencv"].options.xfeatures2d:
            self.cpp_info.requires.append("opencv::opencv_xfeatures2d")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
