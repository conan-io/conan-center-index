from conan.tools.microsoft import is_msvc
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.45.0"


class DlibConan(ConanFile):
    name = "dlib"
    description = "A toolkit for making real world machine learning and data analysis applications"
    topics = ("machine-learning", "deep-learning", "computer-vision")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://dlib.net"
    license = "BSL-1.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_gif": [True, False],
        "with_jpeg": [True, False],
        "with_png": [True, False],
        "with_sse2": [True, False, "auto"],
        "with_sse4": [True, False, "auto"],
        "with_avx": [True, False, "auto"],
        "with_openblas": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_gif": False,  # Doesn't work out-of-the-box with MSVC
        "with_jpeg": True,
        "with_png": True,
        "with_sse2": "auto",
        "with_sse4": "auto",
        "with_avx": "auto",
        "with_openblas": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"

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
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_gif:
            self.requires("giflib/5.2.1")
        if self.options.with_jpeg:
            self.requires("libjpeg/9d")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_openblas:
            self.requires("openblas/0.3.17")

    def validate(self):
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration("dlib can not be built as a shared library with Visual Studio")
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("dlib doesn't support macOS M1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)

        # With in-project builds dlib is always built as a static library,
        # we want to be able to build it as a shared library too
        cmake.definitions["DLIB_IN_PROJECT_BUILD"] = False

        # Configure external dependencies
        cmake.definitions["DLIB_GIF_SUPPORT"] = self.options.with_gif
        cmake.definitions["DLIB_JPEG_SUPPORT"] = self.options.with_jpeg
        cmake.definitions["DLIB_PNG_SUPPORT"] = self.options.with_png

        # Configure SIMD options if possible
        if self.settings.arch in ["x86", "x86_64"]:
            if self.options.with_sse2 != "auto":
                cmake.definitions["USE_SSE2_INSTRUCTIONS"] = self.options.with_sse2
            if self.options.with_sse4 != "auto":
                cmake.definitions["USE_SSE4_INSTRUCTIONS"] = self.options.with_sse4
            if self.options.with_avx != "auto":
                cmake.definitions["USE_AVX_INSTRUCTIONS"] = self.options.with_avx

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

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
        self.cpp_info.set_property("cmake_file_name", "dlib")
        self.cpp_info.set_property("cmake_target_name", "dlib::dlib")
        self.cpp_info.set_property("pkg_config_name", "dlib-1")
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "winmm", "comctl32", "gdi32", "imm32"]

        self.cpp_info.names["pkg_config"] = "dlib-1"
