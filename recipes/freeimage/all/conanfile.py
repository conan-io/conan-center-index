from conan import ConanFile, tools
from conans import CMake
import functools
import os

required_conan_version = ">=1.43.0"


class FreeImageConan(ConanFile):
    name = "freeimage"
    description = "Open Source library project for developers who would like to support popular graphics image formats"\
                  "like PNG, BMP, JPEG, TIFF and others as needed by today's multimedia applications."
    homepage = "https://freeimage.sourceforge.io"
    url = "https://github.com/conan-io/conan-center-index"
    license = "FreeImage", "GPL-3.0-or-later", "GPL-2.0-or-later"
    topics = ("freeimage", "image", "decoding", "graphics")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo"],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_jpeg2000": [True, False],
        "with_openexr": [True, False],
        "with_eigen": [True, False],
        "with_webp": [True, False],
        "with_raw": [True, False],
        "with_jxr": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jpeg": "libjpeg",
        "with_png": True,
        "with_tiff": True,
        "with_jpeg2000": True,
        "with_openexr": True,
        "with_eigen": True,
        "with_webp": True,
        "with_raw": True,
        "with_jxr": True,
    }

    short_paths = True
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        self.output.warn("G3 plugin and JPEGTransform are disabled.")
        if bool(self.options.with_jpeg):
            if self.options.with_tiff:
                self.options["libtiff"].jpeg = self.options.with_jpeg

    def requirements(self):
        self.requires("zlib/1.2.12")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9d")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.2")
        if self.options.with_jpeg2000:
            self.requires("openjpeg/2.5.0")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_webp:
            self.requires("libwebp/1.2.2")
        if self.options.with_tiff or self.options.with_openexr:
            # can't upgrade to openexr/3.x.x because plugin tiff requires openexr/2.x.x header files
            self.requires("openexr/2.5.7")
        if self.options.with_raw:
            self.requires("libraw/0.20.2")
        if self.options.with_jxr:
            self.requires("jxrlib/cci.20170615")
        if self.options.with_tiff:
            self.requires("libtiff/4.3.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, "11")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["FREEIMAGE_WITH_JPEG"] = self.options.with_jpeg != False
        cmake.definitions["FREEIMAGE_WITH_OPENJPEG"] = self.options.with_jpeg2000
        cmake.definitions["FREEIMAGE_WITH_PNG"] = self.options.with_png
        cmake.definitions["FREEIMAGE_WITH_WEBP"] = self.options.with_webp
        cmake.definitions["FREEIMAGE_WITH_OPENEXR"] = self.options.with_openexr
        cmake.definitions["FREEIMAGE_WITH_RAW"] = self.options.with_raw
        cmake.definitions["FREEIMAGE_WITH_JXR"] = self.options.with_jxr
        cmake.definitions["FREEIMAGE_WITH_TIFF"] = self.options.with_tiff
        cmake.configure(build_dir=self._build_subfolder)
        return cmake

    def build(self):
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "Source", "LibPNG"))
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "Source", "LibTIFF4"))
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "Source", "LibOpenJPEG"))
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "Source", "LibJXR"))
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "Source", "LibWebP"))
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "Source", "LibRawLite"))
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "Source", "OpenEXR"))

        for patch in self.conan_data.get("patches", {}).get(self.version, {}):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("license-fi.txt", dst="licenses", src=self._source_subfolder)
        self.copy("license-gplv3.txt", dst="licenses", src=self._source_subfolder)
        self.copy("license-gplv2.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        def imageformats_deps():
            components = []
            components.append("zlib::zlib")
            if self.options.with_jpeg:
                components.append("{0}::{0}".format(self.options.with_jpeg))
            if self.options.with_jpeg2000:
                components.append("openjpeg::openjpeg")
            if self.options.with_png:
                components.append("libpng::libpng")
            if self.options.with_webp:
                components.append("libwebp::libwebp")
            if self.options.with_openexr or self.options.with_tiff:
                components.append("openexr::openexr")
            if self.options.with_raw:
                components.append("libraw::libraw")
            if self.options.with_jxr:
                components.append("jxrlib::jxrlib")
            if self.options.with_tiff:
                components.append("libtiff::libtiff")
            return components

        self.cpp_info.components["FreeImage"].libs = ["freeimage"]
        self.cpp_info.components["FreeImage"].requires = imageformats_deps()
        self.cpp_info.components["FreeImagePlus"].libs = ["freeimageplus"]
        self.cpp_info.components["FreeImagePlus"].requires = ["FreeImage"]

        if not self.options.shared:
            self.cpp_info.components["FreeImage"].defines.append("FREEIMAGE_LIB")
