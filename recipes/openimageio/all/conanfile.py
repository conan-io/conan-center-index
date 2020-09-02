from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class OpenImageIO(ConanFile):
    name = "openimageio"
    description = "OpenImageIO is a library for reading and writing images, and a bunch of related classes, utilities, and applications."
    homepage = "http://www.openimageio.org/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "openimageio", "oiio", "image", "read", "write")
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake", "cmake_find_package"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libjpeg-turbo": [True, False],
        "with_libjpeg": [True, False],
        "with_libpng": [True, False],
        "with_bzip2": [True, False],
        "with_freetype": [True, False],
        "with_hdf5": [True, False],
        "with_opencolorio": [True, False],
        "with_opencv": [True, False],
        "with_tbb": [True, False],
        "with_dcmtk": [True, False],
        "with_ffmpeg": [True, False],
        "with_field3d": [True, False],
        "with_giflib": [True, False],
        "with_libheif": [True, False],
        "with_libraw": [True, False],
        "with_openjpeg": [True, False],
        "with_openvdb": [True, False],
        "with_ptex": [True, False],
        "with_libwebp": [True, False],
        "with_nuke": [True, False],
        "with_qt": [True, False],
        "with_libsquish": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libjpeg-turbo": False,
        "with_libjpeg": True,
        "with_libpng": True,
        "with_bzip2": True,
        "with_freetype": True,
        "with_hdf5": True,
        "with_opencolorio": True,
        "with_opencv": False,
        "with_tbb": True,
        "with_dcmtk": True,
        "with_ffmpeg": False,
        "with_field3d": False,
        "with_giflib": True,
        "with_libheif": False,
        "with_libraw": True,
        "with_openjpeg": True,
        "with_openvdb": False,
        "with_ptex": False,
        "with_libwebp": True,
        "with_nuke": False,
        "with_qt": False,
        "with_libsquish": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("oiio-Release-{}".format(self.version), self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        if self.options.with_libjpeg and self.options.get_safe("with_libjpeg-turbo"):
            raise ConanInvalidConfiguration("enable_libjpeg and libjpeg-turbo cannot be used together")

    def requirements(self):
        self.requires("zlib/1.2.11")
        self.requires("libtiff/4.1.0")
        self.requires("openexr/2.5.2")

        self.requires("boost/1.74.0")

        self.requires("fmt/7.0.3")
        self.requires("pugixml/1.10")
        self.requires("tsl-robin-map/0.6.3")

        if self.options.get_safe("with_libjpeg-turbo", False):
            self.requires("libjpeg-turbo/2.0.5")
        if self.options.with_libjpeg:
            self.requires("libjpeg/9d")
        if self.options.with_libpng:
            self.requires("libpng/1.6.37")
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.with_freetype:
            self.requires("freetype/2.10.2")
        if self.options.with_hdf5:
            self.requires("hdf5/1.12.0")
        if self.options.with_opencolorio:
            self.requires("opencolorio/1.1.1")
        if self.options.with_opencv:
            # FIXME: missing opencv recipe
            raise ConanInvalidConfiguration("opencv is not (yet) available on cci")
        if self.options.with_tbb:
            self.requires("tbb/2020.2")
        if self.options.with_dcmtk:
            self.requires("dcmtk/3.6.5")
        if self.options.with_ffmpeg:
            # FIXME: missing ffmpeg recipe
            raise ConanInvalidConfiguration("ffmpeg is not (yet) available on cci")
        if self.options.with_field3d:
            # FIXME: missing field3d recipe
            raise ConanInvalidConfiguration("field3d is not (yet) available on cci")
        if self.options.with_giflib:
            self.requires("giflib/5.2.1")
        if self.options.with_libheif:
            # FIXME: missing libheif recipe
            raise ConanInvalidConfiguration("libheif is not (yet) available on cci")
        if self.options.with_libraw:
            self.requires("libraw/0.20.0")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.3.1")
        if self.options.with_openvdb:
            # FIXME: missing openvdb recipe
            raise ConanInvalidConfiguration("openvdb is not (yet) available on cci")
        if self.options.with_ptex:
            # FIXME: missing ptex recipe
            raise ConanInvalidConfiguration("ptex is not (yet) available on cci")
        if self.options.with_libwebp:
            self.requires("libwebp/1.1.0")
        if self.options.with_nuke:
            # FIXME: missing nuke recipe
            raise ConanInvalidConfiguration("nuke is not (yet) available on cci")
        if self.options.with_qt:
            # FIXME: missing qt recipe
            raise ConanInvalidConfiguration("qt is not (yet) available on cci")
        if self.options.with_libsquish:
            self.requires("libsquish/1.15")

    @property
    def _deps_information(self):
        information = {}

        def add_to_list(optname, cmakename, enable_override=None):
            enabled = bool(self.options.get_safe("with_{}".format(optname))) if enable_override is None else enable_override
            assert enabled is not None
            information[optname] = {
                "cmake": cmakename,
                "enabled": enabled,
            }

        # First item is the name of the options,
        # Second item is the name of the generated cmake_find_package script.
        # If we could interrogate the generators, this can be automatized.
        add_to_list("libjpeg-turbo",    "libjpeg-turbo")
        add_to_list("libjpeg",          "JPEG")
        add_to_list("libpng",           "PNG")
        add_to_list("bzip2",            "BZip2")
        add_to_list("freetype",         "freetype")
        add_to_list("hdf5",             "HDF5")
        add_to_list("opencolorio",      "OpenColorIO")
        add_to_list("opencv",           "OpenCV")
        add_to_list("tbb",              "TBB")
        add_to_list("dcmtk",            "DCMTK")
        add_to_list("ffmpeg",           "FFmpeg")
        add_to_list("field3d",          "Field3D")
        add_to_list("giflib",           "GIF")
        add_to_list("libheif",          "Libheif")
        add_to_list("libraw",           "LibRaw")
        add_to_list("openjpeg",         "OpenJPEG")
        add_to_list("openvdb",          "OpenVDB")
        add_to_list("ptex",             "PTex")
        add_to_list("libwebp",          "Webp")
        add_to_list("nuke",             "Nuke")
        add_to_list("qt",               "Qt5")
        add_to_list("libsquish",        "libsquish")

        add_to_list("zlib",             "ZLIB",             True)
        add_to_list("libtiff",          "TIFF",             True)
        add_to_list("openexr",          "OpenEXR",          True)
        add_to_list("boost",            "Boost",            True)
        add_to_list("fmt",              "fmt",              True)
        add_to_list("pugixml",          "pugixml",          True)
        add_to_list("tsl-robin-map",    "tsl-robin-map",    True)

        return information

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        dep_information = self._deps_information
        self._cmake = CMake(self)

        for info in dep_information.values():
            self._cmake.definitions["USE_{}".format(info["cmake"].upper())] = info["enabled"]

        self._cmake.definitions["USE_PYTHON"] = False

        self._cmake.definitions["REQUIRED_DEPS"] = ";".join(d["cmake"].upper() for d in dep_information.values() if d["enabled"])

        self._cmake.definitions["OIIO_BUILD_TOOLS"] = True
        self._cmake.definitions["BUILD_DOCS"] = False
        self._cmake.definitions["INSTALL_FONTS"] = False

        self._cmake.definitions["USE_EXTERNAL_PUGIXML"] = True
        self._cmake.definitions["USE_EMBEDDED_LIBSQUISH"] = False

        self._cmake.definitions["BUILD_MISSING_FMT"] = False
        self._cmake.definitions["BUILD_MISSING_ROBINMAP"] = False

        self._cmake.definitions["OIIO_INSTALL_DOCS"] = False
        self._cmake.definitions["OIIO_BUILD_TESTS"] = False
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.filenames["cmake_find_package"] = "OpenImageIO"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenImageIO"
        self.cpp_info.names["cmake_find_package"] = "OpenImageIO"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenImageIO"

        self.cpp_info.components["OpenImageIO_Util"].libs = ["OpenImageIO_Util"]
        self.cpp_info.components["OpenImageIO_Util"].names["cmake_find_package"] = "OpenImageIO_Util"
        self.cpp_info.components["OpenImageIO_Util"].names["cmake_find_package_multi"] = "OpenImageIO_Util"

        self.cpp_info.components["OpenImageIO"].libs = ["OpenImageIO"]
        self.cpp_info.components["OpenImageIO"].names["cmake_find_package"] = "OpenImageIO"
        self.cpp_info.components["OpenImageIO"].names["cmake_find_package_multi"] = "OpenImageIO"
        self.cpp_info.components["OpenImageIO"].names["pkg_config"] = "OpenImageIO"

        if not self.options.shared:
            self.cpp_info.components["OpenImageIO_Util"].defines = ["OIIO_STATIC_DEFINE=1"]
            self.cpp_info.components["OpenImageIO"].defines = ["OIIO_STATIC_DEFINE=1"]

        for conan_name, info in self._deps_information.items():
            if info["enabled"]:
                req = "{0}::{0}".format(conan_name)
                self.cpp_info.components["OpenImageIO_Util"].requires.append(req)
                self.cpp_info.components["OpenImageIO"].requires.append(req)

        # FIXME: openimageio creates the following imported executable targets:
        # - OpenImageIO::iconvert
        # - OpenImageIO::idiff
        # - OpenImageIO::igrep
        # - OpenImageIO::iinfo
        # - OpenImageIO::maketx
        # - OpenImageIO::oiiotool

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
