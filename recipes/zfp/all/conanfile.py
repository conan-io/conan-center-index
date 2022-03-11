import os
from conans import ConanFile, tools, CMake


class ZfpConan(ConanFile):
    name = "zfp"
    description = "Compressed numerical arrays that support high-speed random access"
    homepage = "https://github.com/LLNL/zfp"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    topics = ("conan", "zfp", "compression", "arrays")
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
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
        if self.options.with_cuda:
            self.output.warn("Conan package for CUDA is not available, this package will be used from system.")
        if self.options.with_openmp:
            self.output.warn("Conan package for OpenMP is not available, this package will be used from system.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "zfp-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_CFP"] = True
        self._cmake.definitions["BUILD_UTILITIES"] = False
        self._cmake.definitions["ZFP_WITH_CUDA"] = self.options.with_cuda
        self._cmake.definitions["ZFP_BIT_STREAM_WORD_SIZE"] = self.options.bit_stream_word_size
        self._cmake.definitions["ZFP_WITH_BIT_STREAM_STRIDED"] = self.options.with_bit_stream_strided
        self._cmake.definitions["ZFP_WITH_ALIGNED_ALLOC"] = self.options.with_aligned_alloc
        self._cmake.definitions["ZFP_WITH_CACHE_TWOWAY"] = self.options.with_cache_twoway
        self._cmake.definitions["ZFP_WITH_CACHE_FAST_HASH"] = self.options.with_cache_fast_hash
        self._cmake.definitions["ZFP_WITH_CACHE_PROFILE"] = self.options.with_cache_profile
        self._cmake.definitions["ZFP_WITH_CUDA"] = self.options.with_cuda
        self._cmake.definitions["ZFP_WITH_OPENMP"] = self.options.with_openmp
        if self.settings.os != "Windows" and not self.options.shared:
            self._cmake.definitions["ZFP_ENABLE_PIC"] = self.options.fPIC
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if not self.options.shared and self.options.with_openmp:
            openmp_flags = []
            if self.settings.compiler in ("Visual Studio", "msvc"):
                openmp_flags = ["-openmp"]
            elif self.settings.compiler in ("gcc", "clang"):
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler == "apple-clang":
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]

            self.cpp_info.components["_zfp"].sharedlinkflags = openmp_flags
            self.cpp_info.components["_zfp"].exelinkflags = openmp_flags

        # zfp
        self.cpp_info.components["_zfp"].names["cmake_find_package"] = "zfp"
        self.cpp_info.components["_zfp"].names["cmake_find_package_multi"] = "zfp"
        self.cpp_info.components["_zfp"].libs = ["zfp"]
        # cfp
        self.cpp_info.components["cfp"].names["cmake_find_package"] = "cfp"
        self.cpp_info.components["cfp"].names["cmake_find_package_multi"] = "cfp"
        self.cpp_info.components["cfp"].libs = ["cfp"]
        self.cpp_info.components["cfp"].requires = ["_zfp"]
