from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
import os

required_conan_version = ">=1.47.0"


class FFTWConan(ConanFile):
    name = "fftw"
    description = "C subroutine library for computing the Discrete Fourier Transform (DFT) in one or more dimensions"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.fftw.org/"
    license = "GPL-2.0"
    topics = ("fftw", "dft", "dct", "dst")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "precision": ["double", "single", "longdouble"],
        "openmp": [True, False],
        "threads": [True, False],
        "combinedthreads": [True, False],
        "simd": ["sse", "sse2", "avx", "avx2", False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "precision": "double",
        "openmp": False,
        "threads": False,
        "combinedthreads": False,
        "simd": False,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass
        if not self.options.threads:
            del self.options.combinedthreads

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            if self.options.openmp:
                raise ConanInvalidConfiguration("Shared fftw with openmp can't be built on Windows")
            if self.options.threads and not self.options.combinedthreads:
                raise ConanInvalidConfiguration("Shared fftw with threads and not combinedthreads can't be built on Windows")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.variables["ENABLE_OPENMP"] = self.options.openmp
        tc.variables["ENABLE_THREADS"] = self.options.threads
        tc.variables["WITH_COMBINED_THREADS"] = self.options.get_safe("combinedthreads", False)
        tc.variables["ENABLE_FLOAT"] = self.options.precision == "single"
        tc.variables["ENABLE_LONG_DOUBLE"] = self.options.precision == "longdouble"
        tc.variables["ENABLE_SSE"] = self.options.simd == "sse"
        tc.variables["ENABLE_SSE2"] = self.options.simd == "sse2"
        tc.variables["ENABLE_AVX"] = self.options.simd == "avx"
        tc.variables["ENABLE_AVX2"] = self.options.simd == "avx2"
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYRIGHT", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

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

        # TODO: back to global scope in conan v2 once cmake_find_package_* & pkg_config generators removed
        if self.options.openmp:
            self.cpp_info.components["fftwlib"].libs.append(lib_name + "_omp")
        if self.options.threads and not self.options.combinedthreads:
            self.cpp_info.components["fftwlib"].libs.append(lib_name + "_threads")
        self.cpp_info.components["fftwlib"].libs.append(lib_name)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["fftwlib"].system_libs.append("m")
            if self.options.threads:
                self.cpp_info.components["fftwlib"].system_libs.append("pthread")

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.filenames["cmake_find_package"] = cmake_config_name
        self.cpp_info.filenames["cmake_find_package_multi"] = cmake_config_name
        self.cpp_info.names["cmake_find_package"] = cmake_namespace
        self.cpp_info.names["cmake_find_package_multi"] = cmake_namespace
        self.cpp_info.components["fftwlib"].names["cmake_find_package"] = cmake_target_name
        self.cpp_info.components["fftwlib"].names["cmake_find_package_multi"] = cmake_target_name
        self.cpp_info.components["fftwlib"].set_property("cmake_target_name", "{}::{}".format(cmake_namespace, cmake_target_name))
        self.cpp_info.components["fftwlib"].set_property("pkg_config_name", pkgconfig_name)

    @property
    def _prec_suffix(self):
        return {
            "double": "",
            "single": "f",
            "longdouble": "l"
        }
