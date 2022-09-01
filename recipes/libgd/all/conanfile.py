from conan.tools.microsoft import is_msvc
from conans import ConanFile, tools, CMake
import os

required_conan_version = ">=1.45.0"


class LibgdConan(ConanFile):
    name = "libgd"
    license = "BSD-like"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("GD is an open source code library for the dynamic "
                   "creation of images by programmers.")
    topics = ("images", "graphics")
    homepage = "https://libgd.github.io"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
        "with_jpeg": [True, False],
        "with_tiff": [True, False],
        "with_freetype": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_png": False,
        "with_jpeg": False,
        "with_tiff": False,
        "with_freetype": False,
    }

    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"
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

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
            if is_msvc(self):
                self.requires("getopt-for-visual-studio/20200201")
        if self.options.with_jpeg:
            self.requires("libjpeg/9d")
        if self.options.with_tiff:
            self.requires("libtiff/4.3.0")
        if self.options.with_freetype:
            self.requires("freetype/2.11.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(cmakelists, "${CMAKE_SOURCE_DIR}", "${CMAKE_CURRENT_SOURCE_DIR}")
        tools.replace_in_file(cmakelists,
                              "SET(CMAKE_MODULE_PATH \"${GD_SOURCE_DIR}/cmake/modules\")",
                              "LIST(APPEND CMAKE_MODULE_PATH \"${GD_SOURCE_DIR}/cmake/modules\")")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "CMakeLists.txt"),
                              "RUNTIME DESTINATION bin",
                              "RUNTIME DESTINATION bin BUNDLE DESTINATION bin")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared
        if tools.Version(self.version) >= "2.3.0":
            self._cmake.definitions["ENABLE_GD_FORMATS"] = True
        self._cmake.definitions["ENABLE_PNG"] = self.options.with_png
        self._cmake.definitions["ENABLE_LIQ"] = False
        self._cmake.definitions["ENABLE_JPEG"] = self.options.with_jpeg
        self._cmake.definitions["ENABLE_TIFF"] = self.options.with_tiff
        self._cmake.definitions["ENABLE_ICONV"] = False
        self._cmake.definitions["ENABLE_XPM"] = False
        self._cmake.definitions["ENABLE_FREETYPE"] = self.options.with_freetype
        self._cmake.definitions["ENABLE_FONTCONFIG"] = False
        self._cmake.definitions["ENABLE_WEBP"] = False
        if tools.Version(self.version) >= "2.3.2":
            self._cmake.definitions["ENABLE_HEIF"] = False
            self._cmake.definitions["ENABLE_AVIF"] = False
        if tools.Version(self.version) >= "2.3.0":
            self._cmake.definitions["ENABLE_RAQM"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"]= "gdlib"
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("BGD_NONDLL")
            self.cpp_info.defines.append("BGDWIN32")
        if self.settings.os in ("FreeBSD", "Linux", "Android", "SunOS", "AIX"):
            self.cpp_info.system_libs.append("m")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
