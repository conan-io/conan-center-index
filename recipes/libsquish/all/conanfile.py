import os

from conans import ConanFile, CMake, tools

class LibsquishConan(ConanFile):
    name = "libsquish"
    description = "The libSquish library compresses images with the DXT " \
                  "standard (also known as S3TC)."
    license = "MIT"
    topics = ("conan", "libsquish", "image", "compression", "dxt", "s3tc")
    homepage = "https://sourceforge.net/projects/libsquish"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "openmp": [True, False],
        "sse2_intrinsics": [True, False],
        "altivec_intrinsics": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "openmp": False,
        "sse2_intrinsics": False,
        "altivec_intrinsics": False
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _sse2_compliant_archs(self):
        return ["x86", "x86_64"]

    @property
    def _altivec_compliant_archs(self):
        return ["ppc32be", "ppc32", "ppc64le", "ppc64"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in self._sse2_compliant_archs:
            del self.options.sse2_intrinsics
        if self.settings.arch not in self._altivec_compliant_archs:
            del self.options.altivec_intrinsics

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_SQUISH_WITH_OPENMP"] = self.options.openmp
        self._cmake.definitions["BUILD_SQUISH_WITH_SSE2"] = self.options.get_safe("sse2_intrinsics") or False
        self._cmake.definitions["BUILD_SQUISH_WITH_ALTIVEC"] = self.options.get_safe("altivec_intrinsics") or False
        self._cmake.definitions["BUILD_SQUISH_EXTRA"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
