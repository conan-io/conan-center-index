from conans import ConanFile, CMake, tools
import os
import shutil

required_conan_version = ">=1.43.0"


class FreeImageConan(ConanFile):
    name = "freeimage"
    description = "Open Source library project for developers who would like to support popular graphics image formats"\
                  "like PNG, BMP, JPEG, TIFF and others as needed by today's multimedia applications."
    homepage = "https://freeimage.sourceforge.io"
    url = "https://github.com/conan-io/conan-center-index"
    license = "FreeImage", "GPL-3.0-or-later", "GPL-2.0-or-later"
    topics = ("freeimage", "image", "decoding", "graphics")
    generators = "cmake", "cmake_find_package"
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

    _cmake = None

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
        tools.check_min_cppstd(self, "11")
        if self.options.shared:
            del self.options.fPIC
        self.output.warn("G3 plugin and JPEGTransform are disabled.")
        if self.options.with_jpeg is not None:
            if self.options.with_tiff:
                self.options["libtiff"].jpeg = self.options.with_jpeg

    def requirements(self):
        self.requires("zlib/1.2.11")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9d")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.2")
        if self.options.with_jpeg2000:
            self.requires("openjpeg/2.4.0")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_webp:
            self.requires("libwebp/1.2.2")
        if self.options.with_openexr:
            self.requires("openexr/2.5.7")
        if self.options.with_raw:
            self.requires("libraw/0.20.2")
        if self.options.with_jxr:
            self.requires("jxrlib/cci.20170615")
        if self.options.with_tiff:
            self.requires("libtiff/4.3.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_JPEG"] = self.options.with_jpeg != False
        self._cmake.definitions["WITH_OPENJPEG"] = self.options.with_jpeg2000
        self._cmake.definitions["WITH_PNG"] = self.options.with_png
        self._cmake.definitions["WITH_WEBP"] = self.options.with_webp
        self._cmake.definitions["WITH_OPENEXR"] = self.options.with_openexr
        self._cmake.definitions["WITH_RAW"] = self.options.with_raw
        self._cmake.definitions["WITH_JXR"] = self.options.with_jxr
        self._cmake.definitions["WITH_TIFF"] = self.options.with_tiff
        self._cmake.configure(build_dir=self._build_subfolder)
        return self._cmake

    def build(self):
        tools.rmdir(os.path.join(self._source_subfolder, "Source", "LibPNG"))
        tools.rmdir(os.path.join(self._source_subfolder, "Source", "LibTIFF4"))
        tools.rmdir(os.path.join(self._source_subfolder, "Source", "LibOpenJPEG"))
        tools.rmdir(os.path.join(self._source_subfolder, "Source", "LibJXR"))
        tools.rmdir(os.path.join(self._source_subfolder, "Source", "LibWebP"))
        tools.rmdir(os.path.join(self._source_subfolder, "Source", "LibRawLite"))
        tools.rmdir(os.path.join(self._source_subfolder, "Source", "OpenEXR"))

        for patch in self.conan_data.get("patches", {}).get(self.version, {}):
            tools.patch(**patch)
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
            if self.options.with_openexr:
                components.append("openexr::openexr")
            if self.options.with_raw:
                components.append("libraw::libraw")
            if self.options.with_jxr:
                components.append("jxrlib::jxrlib")
            if self.options.with_tiff:
                components.append("libtiff::libtiff")
            return components

        self.cpp_info.names["pkg_config"] = "freeimage"
        self.cpp_info.names["cmake_find_package"] = "FreeImage"
        self.cpp_info.names["cmake_find_package_multi"] = "FreeImage"
        self.cpp_info.components["FreeImage"].libs = ["freeimage"]
        self.cpp_info.components["FreeImage"].requires = imageformats_deps()
        self.cpp_info.components["FreeImagePlus"].libs = ["freeimageplus"]
        self.cpp_info.components["FreeImagePlus"].requires = ["FreeImage"]

        if not self.options.shared:
            self.cpp_info.components["FreeImage"].defines.append("FREEIMAGE_LIB")
