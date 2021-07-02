import glob
import os

from conans import ConanFile, CMake, tools

class CfitsioConan(ConanFile):
    name = "cfitsio"
    description = "C library for reading and writing data files in FITS " \
                  "(Flexible Image Transport System) data format"
    license = "ISC"
    topics = ("conan", "cfitsio", "fits", "image", "nasa", "astronomy", "astrophysics", "space")
    homepage = "https://heasarc.gsfc.nasa.gov/fitsio/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threadsafe": [True, False],
        "simd_intrinsics": [None, "sse2", "ssse3"],
        "with_bzip2": [True, False],
        "with_curl": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threadsafe": False,
        "simd_intrinsics": None,
        "with_bzip2": False,
        "with_curl": False
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.simd_intrinsics
        if self.settings.os == "Windows":
            del self.options.with_bzip2
            del self.options.with_curl

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.threadsafe and self.settings.os == "Windows" and \
           (not self.settings.compiler == "gcc" or self.settings.compiler.threads == "win32"):
            self.requires("pthreads4w/3.0.0")
        if self.options.get_safe("with_bzip2"):
            self.requires("bzip2/1.0.8")
        if self.options.get_safe("with_curl"):
            self.requires("libcurl/7.73.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("cfitsio-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # Remove embedded zlib files
        for zlib_file in glob.glob(os.path.join(self._source_subfolder, "zlib", "*")):
            if not zlib_file.endswith(("zcompress.c", "zuncompress.c")):
                os.remove(zlib_file)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["USE_PTHREADS"] = self.options.threadsafe
        self._cmake.definitions["CFITSIO_USE_SSE2"] = self.options.get_safe("simd_intrinsics") == "sse2"
        self._cmake.definitions["CFITSIO_USE_SSSE3"] = self.options.get_safe("simd_intrinsics") == "ssse3"
        if self.settings.os != "Windows":
            self._cmake.definitions["CFITSIO_USE_BZIP2"] = self.options.with_bzip2
            self._cmake.definitions["UseCurl"] = self.options.with_curl
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("License.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["cfitsio"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
            if self.options.threadsafe:
                self.cpp_info.system_libs.append("pthread")
