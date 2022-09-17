from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.50.0"


class ZfpConan(ConanFile):
    name = "zfp"
    description = "Compressed numerical arrays that support high-speed random access"
    homepage = "https://github.com/LLNL/zfp"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    topics = ("zfp", "compression", "arrays")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "bit_stream_word_size": [8,16,32,64],
        "with_cuda": [True, False],
        "with_bit_stream_strided": [True, False],
        "with_aligned_alloc": [True, False],
        "with_cache_twoway": [True, False],
        "with_cache_fast_hash": [True, False],
        "with_cache_profile": [True, False],
        "with_openmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "bit_stream_word_size": 64,
        "with_cuda": False,
        "with_bit_stream_strided": False,
        "with_aligned_alloc": False,
        "with_cache_twoway": False,
        "with_cache_fast_hash": False,
        "with_cache_profile": False,
        "with_openmp": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.info.options.with_cuda:
            self.output.warn("Conan package for CUDA is not available, this package will be used from system.")
        if self.info.options.with_openmp:
            self.output.warn("Conan package for OpenMP is not available, this package will be used from system.")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_CFP"] = True
        tc.variables["BUILD_UTILITIES"] = False
        tc.variables["ZFP_WITH_CUDA"] = self.options.with_cuda
        tc.variables["ZFP_BIT_STREAM_WORD_SIZE"] = self.options.bit_stream_word_size
        tc.variables["ZFP_WITH_BIT_STREAM_STRIDED"] = self.options.with_bit_stream_strided
        tc.variables["ZFP_WITH_ALIGNED_ALLOC"] = self.options.with_aligned_alloc
        tc.variables["ZFP_WITH_CACHE_TWOWAY"] = self.options.with_cache_twoway
        tc.variables["ZFP_WITH_CACHE_FAST_HASH"] = self.options.with_cache_fast_hash
        tc.variables["ZFP_WITH_CACHE_PROFILE"] = self.options.with_cache_profile
        tc.variables["ZFP_WITH_CUDA"] = self.options.with_cuda
        tc.variables["ZFP_WITH_OPENMP"] = self.options.with_openmp
        if self.settings.os != "Windows" and not self.options.shared:
            tc.variables["ZFP_ENABLE_PIC"] = self.options.fPIC
        tc.variables["BUILD_TESTING"] = False
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "zfp")
        # to avoid to create an unwanted target, since we can't allow zfp::zfp to be the global target here
        self.cpp_info.set_property("cmake_target_name", "zfp::cfp")

        # zfp
        self.cpp_info.components["_zfp"].set_property("cmake_target_name", "zfp::zfp")
        self.cpp_info.components["_zfp"].libs = ["zfp"]

        # cfp
        self.cpp_info.components["cfp"].set_property("cmake_target_name", "zfp::cfp")
        self.cpp_info.components["cfp"].libs = ["cfp"]
        self.cpp_info.components["cfp"].requires = ["_zfp"]

        if not self.options.shared and self.options.with_openmp:
            openmp_flags = []
            if is_msvc(self):
                openmp_flags = ["-openmp"]
            elif self.settings.compiler in ("gcc", "clang"):
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler == "apple-clang":
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]

            self.cpp_info.components["_zfp"].sharedlinkflags = openmp_flags
            self.cpp_info.components["_zfp"].exelinkflags = openmp_flags

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["_zfp"].names["cmake_find_package"] = "zfp"
        self.cpp_info.components["_zfp"].names["cmake_find_package_multi"] = "zfp"
