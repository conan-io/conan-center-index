from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os, shutil

class OpenImageIOConan(ConanFile):
    name = "openimageio"
    description = "OpenImageIO is a library for reading and writing images, and a bunch of related classes, utilities, and applications." \
                  "There is a particular emphasis on formats and functionality used in professional, large-scale animation and visual effects work for film."
    topics = ("vfx", "image", "picture")
    license = "BSD-3-Clause"
    homepage = "http://www.openimageio.org/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    short_paths = True

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo"],
        "with_libpng": [True, False],
        "with_freetype": [True, False],
        "with_hdf5": [True, False],
        "with_opencolorio": [True, False],
        "with_opencv": [True, False],
        "with_tbb": [True, False],
        "with_dicom": [True, False],
        "with_ffmpeg": [True, False],
        "with_giflib": [True, False],
        "with_libheif": [True, False],
        "with_raw": [True, False],
        "with_openjpeg": [True, False],
        "with_openvdb": [True, False],
        "with_ptex": [True, False],
        "with_libwebp": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libjpeg": "libjpeg",
        "with_libpng": True,
        "with_freetype": True,
        "with_hdf5": True,
        "with_opencolorio": True,
        "with_opencv": True,
        "with_tbb": True,
        "with_dicom": False, # Heavy dependency, disabled by default
        "with_ffmpeg": True,
        "with_giflib": True,
        "with_libheif": True,
        "with_raw": False, # libraw is available under CDDL-1.0 or LGPL-2.1, for this reason it is disabled by default
        "with_openjpeg": True,
        "with_openvdb": False, # FIXME: broken on M1
        "with_ptex": True,
        "with_libwebp": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)

        # CMake options
        self._cmake.definitions["CMAKE_DEBUG_POSTFIX"] = "" # Needed for 2.3.x.x+ versions
        self._cmake.definitions["OIIO_BUILD_TOOLS"] = True
        self._cmake.definitions["OIIO_BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_DOCS"] = False
        self._cmake.definitions["INSTALL_DOCS"] = False
        self._cmake.definitions["INSTALL_FONTS"] = False
        self._cmake.definitions["INSTALL_CMAKE_HELPER"] = False
        self._cmake.definitions["EMBEDPLUGINS"] = True
        self._cmake.definitions["USE_PYTHON"] = False
        self._cmake.definitions["USE_EXTERNAL_PUGIXML"] = True

        # OIIO CMake files are patched to check USE_* flags to require or not use dependencies
        self._cmake.definitions["USE_JPEGTURBO"] = self.options.with_libjpeg == "libjpeg-turbo"
        self._cmake.definitions["USE_JPEG"] = True # Needed for jpeg.imageio plugin, libjpeg/libjpeg-turbo selection still works
        self._cmake.definitions["USE_HDF5"] = self.options.with_hdf5
        self._cmake.definitions["USE_OPENCOLORIO"] = self.options.with_opencolorio
        self._cmake.definitions["USE_OPENCV"] = self.options.with_opencv
        self._cmake.definitions["USE_TBB"] = self.options.with_tbb
        self._cmake.definitions["USE_DCMTK"] = self.options.with_dicom
        self._cmake.definitions["USE_FFMPEG"] = self.options.with_ffmpeg
        self._cmake.definitions["USE_FIELD3D"] = False
        self._cmake.definitions["USE_GIF"] = self.options.with_giflib
        self._cmake.definitions["USE_LIBHEIF"] = self.options.with_libheif
        self._cmake.definitions["USE_LIBRAW"] = self.options.with_raw
        self._cmake.definitions["USE_OPENVDB"] = self.options.with_openvdb
        self._cmake.definitions["USE_PTEX"] = self.options.with_ptex
        self._cmake.definitions["USE_R3DSDK"] = False
        self._cmake.definitions["USE_NUKE"] = False
        self._cmake.definitions["USE_OPENGL"] = False
        self._cmake.definitions["USE_QT"] = False
        self._cmake.definitions["USE_LIBPNG"] = self.options.with_libpng
        self._cmake.definitions["USE_FREETYPE"] = self.options.with_freetype
        self._cmake.definitions["USE_LIBWEBP"] = self.options.with_libwebp
        self._cmake.definitions["USE_OPENJPEG"] = self.options.with_openjpeg

        if self.options.with_openvdb:
            self._cmake.definitions["CMAKE_CXX_STANDARD"] = 14

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        # Required libraries
        self.requires("zlib/1.2.11")
        self.requires("boost/1.76.0")
        self.requires("libtiff/4.3.0")
        self.requires("openexr/2.5.7")
        if self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9d")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.1")
        self.requires("pugixml/1.11")
        self.requires("libsquish/1.15")
        self.requires("tsl-robin-map/0.6.3")
        self.requires("libsquish/1.15")
        self.requires("fmt/8.0.1")

        # Optional libraries
        if self.options.with_libpng:
            self.requires("libpng/1.6.37")
        if self.options.with_freetype:
            self.requires("freetype/2.11.0")
        if self.options.with_hdf5:
            self.requires("hdf5/1.12.0")
        if self.options.with_opencolorio:
            self.requires("opencolorio/1.1.1")
        if self.options.with_opencv:
            self.requires("opencv/4.5.3")
        if self.options.with_tbb:
            self.requires("tbb/2020.3")
        if self.options.with_dicom:
            self.requires("dcmtk/3.6.6")
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/4.2.1")
        # TODO: Field3D dependency
        if self.options.with_giflib:
            self.requires("giflib/5.2.1")
        if self.options.with_libheif:
            self.requires("libheif/1.12.0")
        if self.options.with_raw:
            self.requires("libraw/0.20.2")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.4.0")
        if self.options.with_openvdb:
            self.requires("openvdb/8.0.1")
        if self.options.with_ptex:
            self.requires("ptex/2.4.0")
        if self.options.with_libwebp:
            self.requires("libwebp/1.2.1")
        # TODO: R3DSDK dependency
        # TODO: Nuke dependency

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            if tools.Version(self.version) >= "2.3.0.0" or self.options.with_openvdb:
                tools.check_min_cppstd(self, 14)
            else:
                tools.check_min_cppstd(self, 11)
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.get_safe("runtime", "").startswith("MT") and self.options.shared:
            raise ConanInvalidConfiguration("Building shared library with static runtime is not supported!")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
         for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "OpenImageIO"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenImageIO"

        self.cpp_info.components["util"].libs = ["OpenImageIO_Util"]
        self.cpp_info.components["util"].requires = ["boost::filesystem", "boost::thread", "boost::system", "boost::regex", "openexr::openexr"]
        if self.settings.os == "Linux":
            self.cpp_info.components["util"].system_libs.extend(["dl", "m", "pthread"])

        self.cpp_info.components["main"].libs = ["OpenImageIO"]
        self.cpp_info.components["main"].requires = [
            "util", "zlib::zlib", "boost::thread", "boost::system", "boost::container", "boost::regex", "libtiff::libtiff", "openexr::openexr",
            "pugixml::pugixml", "tsl-robin-map::tsl-robin-map", "libsquish::libsquish", "fmt::fmt"]
        if self.options.with_libjpeg == "libjpeg":
            self.cpp_info.components["main"].requires.append("libjpeg::libjpeg")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.cpp_info.components["main"].requires.append("libjpeg-turbo::libjpeg-turbo")
        if self.options.with_libpng:
            self.cpp_info.components["main"].requires.append("libpng::libpng")
        if self.options.with_freetype:
            self.cpp_info.components["main"].requires.append("freetype::freetype")
        if self.options.with_hdf5:
            self.cpp_info.components["main"].requires.append("hdf5::hdf5")
        if self.options.with_opencolorio:
            self.cpp_info.components["main"].requires.append("opencolorio::opencolorio")
        if self.options.with_opencv:
            self.cpp_info.components["main"].requires.append("opencv::opencv")
        if self.options.with_tbb:
            self.cpp_info.components["main"].requires.append("tbb::tbb")
        if self.options.with_dicom:
            self.cpp_info.components["main"].requires.append("dcmtk::dcmtk")
        if self.options.with_ffmpeg:
            self.cpp_info.components["main"].requires.append("ffmpeg::ffmpeg")
        if self.options.with_giflib:
            self.cpp_info.components["main"].requires.append("giflib::giflib")
        if self.options.with_libheif:
            self.cpp_info.components["main"].requires.append("libheif::libheif")
        if self.options.with_raw:
            self.cpp_info.components["main"].requires.append("libraw::libraw")
        if self.options.with_openjpeg:
            self.cpp_info.components["main"].requires.append("openjpeg::openjpeg")
        if self.options.with_openvdb:
            self.cpp_info.components["main"].requires.append("openvdb::openvdb")
        if self.options.with_ptex:
            self.cpp_info.components["main"].requires.append("ptex::ptex")
        if self.options.with_libwebp:
            self.cpp_info.components["main"].requires.append("libwebp::libwebp")
        if self.settings.os == "Linux":
            self.cpp_info.components["main"].system_libs.extend(["dl", "m", "pthread"])
        self.cpp_info.components["main"].names["pkg_config"] = "OpenImageIO"

        if not self.options.shared:
            self.cpp_info.components["main"].defines.append("OIIO_STATIC_DEFINE")
