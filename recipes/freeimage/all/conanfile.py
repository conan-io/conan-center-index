from conans import ConanFile, CMake, tools
import os
import shutil


class FreeImageConan(ConanFile):
    name = "freeimage"
    description = "Open Source library project for developers who would like to support popular graphics image formats"\
                  "like PNG, BMP, JPEG, TIFF and others as needed by today's multimedia applications."
    homepage = "https://freeimage.sourceforge.io"
    url = "https://github.com/conan-io/conan-center-index"
    license = "FreeImage", "GPL-3.0-or-later", "GPL-2.0-or-later"
    topics = ("conan", "freeimage", "image", "decoding", "graphics")
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
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
        tools.check_min_cppstd(self, "11")
        if self.options.shared:
            del self.options.fPIC
        self.output.warn("TIFF and G3 plugins are disabled.")

    def requirements(self):
        self.requires("zlib/1.2.11")
        self.requires("libjpeg/9d")
        self.requires("openjpeg/2.3.1")
        self.requires("libpng/1.6.37")
        self.requires("libwebp/1.1.0")
        self.requires("openexr/2.5.2 ")
        self.requires("libraw/0.19.5")
        self.requires("jxrlib/cci.20170615")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "FreeImage"
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
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
        self.cpp_info.name = "freeimage"
        self.cpp_info.names["pkg_config"] = "freeimage"
        self.cpp_info.names["cmake_find_package"] = "FreeImage"
        self.cpp_info.names["cmake_find_package_multi"] = "FreeImage"
        self.cpp_info.components["FreeImagePlus"].libs = ["freeimageplus"]
        self.cpp_info.components["FreeImagePlus"].requires = ["freeimage"]

        if not self.options.shared:
            self.cpp_info.defines.append("FREEIMAGE_LIB")
