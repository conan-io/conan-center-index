from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"

class FFTWConan(ConanFile):
    name = "fftw"
    description = "C subroutine library for computing the Discrete Fourier Transform (DFT) in one or more dimensions"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.fftw.org/"
    license = "GPL-2.0"
    topics = ("conan", "fftw", "dft", "dct", "dst")
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "precision": ["double", "single", "longdouble"],
               "openmp": [True, False],
               "threads": [True, False],
               "combinedthreads": [True, False],
               "simd": ["sse", "sse2", "avx", "avx2", False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "precision": "double",
                       "openmp": False,
                       "threads": False,
                       "combinedthreads": False,
                       "simd": False}

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if not self.options.threads:
            del self.options.combinedthreads
        if self.settings.os == "Windows" and self.options.shared:
            if self.options.openmp:
                raise ConanInvalidConfiguration("Shared fftw with openmp can't be built on Windows")
            if self.options.threads and not self.options.combinedthreads:
                raise ConanInvalidConfiguration("Shared fftw with threads and not combinedthreads can't be built on Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["ENABLE_OPENMP"] = self.options.openmp
        self._cmake.definitions["ENABLE_THREADS"] = self.options.threads
        self._cmake.definitions["WITH_COMBINED_THREADS"] = self.options.get_safe("combinedthreads", False)
        self._cmake.definitions["ENABLE_FLOAT"] = self.options.precision == "single"
        self._cmake.definitions["ENABLE_LONG_DOUBLE"] = self.options.precision == "longdouble"
        self._cmake.definitions["ENABLE_SSE"] = self.options.simd == "sse"
        self._cmake.definitions["ENABLE_SSE2"] = self.options.simd == "sse2"
        self._cmake.definitions["ENABLE_AVX"] = self.options.simd == "avx"
        self._cmake.definitions["ENABLE_AVX2"] = self.options.simd == "avx2"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYRIGHT", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        prec_suffix = self._prec_suffix[str(self.options.precision)]
        cmake_config_name = "FFTW3" + prec_suffix
        cmake_namespace = "FFTW3"
        cmake_target_name = "fftw3" + prec_suffix
        pkgconfig_name = "fftw3" + prec_suffix
        lib_name = "fftw3" + prec_suffix
        
        self.cpp_info.set_property("cmake_file_name", cmake_config_name)
        self.cpp_info.set_property("cmake_target_name", "{}::{}".format(cmake_namespace, cmake_target_name))
        self.cpp_info.set_property("pkg_config_name", pkgconfig_name)

        self.cpp_info.filenames["cmake_find_package"] = cmake_config_name
        self.cpp_info.filenames["cmake_find_package_multi"] = cmake_config_name
        self.cpp_info.names["cmake_find_package"] = cmake_namespace
        self.cpp_info.names["cmake_find_package_multi"] = cmake_namespace
        
        self.cpp_info.components["fftwlib"].set_property("cmake_target_name", "{}::{}".format(cmake_namespace, cmake_target_name))
        self.cpp_info.components["fftwlib"].set_property("pkg_config_name", pkgconfig_name)
        
        self.cpp_info.components["fftwlib"].names["cmake_find_package"] = cmake_target_name
        self.cpp_info.components["fftwlib"].names["cmake_find_package_multi"] = cmake_target_name
        if self.options.openmp:
            self.cpp_info.components["fftwlib"].libs.append(lib_name + "_omp")
        if self.options.threads and not self.options.combinedthreads:
            self.cpp_info.components["fftwlib"].libs.append(lib_name + "_threads")
        self.cpp_info.components["fftwlib"].libs.append(lib_name)
        if self.settings.os == "Linux":
            self.cpp_info.components["fftwlib"].system_libs.append("m")
            if self.options.threads:
                self.cpp_info.components["fftwlib"].system_libs.append("pthread")

    @property
    def _prec_suffix(self):
        return {
            "double": "",
            "single": "f",
            "longdouble": "l"
        }
