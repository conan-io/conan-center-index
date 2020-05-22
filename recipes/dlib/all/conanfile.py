import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class DlibConan(ConanFile):
    name = "dlib"
    description = "A toolkit for making real world machine learning and data analysis applications"
    topics = ("machine-learning", "deep-learning", "computer-vision")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://dlib.net"
    license = "BSL-1.0"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_gif": [True, False],
        "with_jpeg": [True, False],
        "with_png": [True, False],
        "with_sse2": [True, False, "auto"],
        "with_sse4": [True, False, "auto"],
        "with_avx": [True, False, "auto"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_gif": False,  # Doesn't work out-of-the-box with MSVC
        "with_jpeg": True,
        "with_png": True,
        "with_sse2": "auto",
        "with_sse4": "auto",
        "with_avx": "auto"
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
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.with_sse2
            del self.options.with_sse4
            del self.options.with_avx

    def configure(self):
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("dlib can not be built as a shared library with Visual Studio")

    def requirements(self):
        if self.options.with_gif:
            self.requires("giflib/5.1.4")
        if self.options.with_jpeg:
            self.requires("libjpeg/9d")
        if self.options.with_png:
            self.requires("libpng/1.6.37")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        # With in-project builds dlib is always built as a static library,
        # we want to be able to build it as a shared library too
        self._cmake.definitions["DLIB_IN_PROJECT_BUILD"] = "OFF"

        # Configure external dependencies
        self._cmake.definitions["DLIB_GIF_SUPPORT"] = self.options.with_gif
        self._cmake.definitions["DLIB_JPEG_SUPPORT"] = self.options.with_jpeg
        self._cmake.definitions["DLIB_PNG_SUPPORT"] = self.options.with_png

        # Configure SIMD options if possible
        if self.settings.arch in ["x86", "x86_64"]:
            if self.options.with_sse2 != "auto":
                self._cmake.definitions["USE_SSE2_INSTRUCTIONS"] = self.options.with_sse2
            if self.options.with_sse4 != "auto":
                self._cmake.definitions["USE_SSE4_INSTRUCTIONS"] = self.options.with_sse4
            if self.options.with_avx != "auto":
                self._cmake.definitions["USE_AVX_INSTRUCTIONS"] = self.options.with_avx

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("LICENSE.txt", "licenses", os.path.join(self._source_subfolder, "dlib"), keep_path=False)

        # Remove configuration files
        for dir_to_remove in [
            os.path.join("lib", "cmake"),
            os.path.join("lib", "pkgconfig"),
            os.path.join("include", "dlib", "cmake_utils"),
            os.path.join("include", "dlib", "external", "pybind11", "tools")
        ]:
            tools.rmdir(os.path.join(self.package_folder, dir_to_remove))

    def package_info(self):
        # There is a single library whose name depends on settings
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
