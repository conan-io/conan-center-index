from conans import ConanFile, CMake, tools
import os


class FFTWConan(ConanFile):
    name = "fftw"
    description = "C subroutine library for computing the Discrete Fourier Transform (DFT) in one or more dimensions"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.fftw.org/"
    license = "GPL-2.0"
    topics = ("conan", "fftw", "dft", "dct", "dst")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "precision": ["double", "single", "longdouble"],
               "openmp": [True, False],
               "threads": [True, False],
               "combinedthreads": [True, False]}
    default_options = {'shared': False,
                       'fPIC': True,
                       'precision': 'double',
                       'openmp': False,
                       'threads': False,
                       'combinedthreads': False}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTS"] = False
        cmake.definitions["ENABLE_OPENMP"] = self.options.openmp
        cmake.definitions["ENABLE_THREADS"] = self.options.threads
        cmake.definitions["WITH_COMBINED_THREADS"] = self.options.combinedthreads
        cmake.definitions["ENABLE_FLOAT"] = self.options.precision == "single"
        cmake.definitions["ENABLE_LONG_DOUBLE"] = self.options.precision == "longdouble"
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYRIGHT", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
