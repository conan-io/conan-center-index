from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.53.0"


class OpenImageIOConan(ConanFile):
    name = "openimageio"
    description = (
        "OpenImageIO is a library for reading and writing images, and a bunch "
        "of related classes, utilities, and applications. There is a "
        "particular emphasis on formats and functionality used in "
        "professional, large-scale animation and visual effects work for film."
    )
    topics = ("vfx", "image", "picture")
    license = "Apache-2.0"
    homepage = "http://www.openimageio.org/"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
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
        "with_opencv": False,
        "with_tbb": False,
        "with_dicom": False,  # Heavy dependency, disabled by default
        "with_ffmpeg": True,
        "with_giflib": True,
        "with_libheif": True,
        "with_raw": False,  # libraw is available under CDDL-1.0 or LGPL-2.1, for this reason it is disabled by default
        "with_openjpeg": True,
        "with_openvdb": False,  # FIXME: broken on M1
        "with_ptex": True,
        "with_libwebp": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        # Required libraries
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("boost/1.83.0")
        self.requires("libtiff/4.6.0")
        self.requires("openexr/3.1.9")
        if self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.0")
        self.requires("pugixml/1.13")
        self.requires("libsquish/1.15")
        self.requires("tsl-robin-map/1.2.1")
        self.requires("fmt/10.1.1")

        # Optional libraries
        if self.options.with_libpng:
            self.requires("libpng/1.6.40")
        if self.options.with_freetype:
            self.requires("freetype/2.13.0")
        if self.options.with_hdf5:
            self.requires("hdf5/1.14.1")
        if self.options.with_opencolorio:
            self.requires("opencolorio/2.2.1")
        if self.options.with_opencv:
            self.requires("opencv/4.5.5")
        if self.options.with_tbb:
            self.requires("onetbb/2021.10.0")
        if self.options.with_dicom:
            self.requires("dcmtk/3.6.7")
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/6.0")
        # TODO: Field3D dependency
        if self.options.with_giflib:
            self.requires("giflib/5.2.1")
        if self.options.with_libheif:
            self.requires("libheif/1.16.2")
        if self.options.with_raw:
            self.requires("libraw/0.21.1")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.0")
        if self.options.with_openvdb:
            self.requires("openvdb/8.0.1")
        if self.options.with_ptex:
            self.requires("ptex/2.4.0")
        if self.options.with_libwebp:
            self.requires("libwebp/1.3.2")
        # TODO: R3DSDK dependency
        # TODO: Nuke dependency

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 14)
        if is_msvc(self) and is_msvc_static_runtime(self) and self.options.shared:
            raise ConanInvalidConfiguration(
                "Building shared library with static runtime is not supported!"
            )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)

        # CMake options
        tc.variables["CMAKE_DEBUG_POSTFIX"] = ""  # Needed for 2.3.x.x+ versions
        tc.variables["OIIO_BUILD_TOOLS"] = True
        tc.variables["OIIO_BUILD_TESTS"] = False
        tc.variables["BUILD_DOCS"] = False
        tc.variables["INSTALL_DOCS"] = False
        tc.variables["INSTALL_FONTS"] = False
        tc.variables["INSTALL_CMAKE_HELPER"] = False
        tc.variables["EMBEDPLUGINS"] = True
        tc.variables["USE_PYTHON"] = False
        tc.variables["USE_EXTERNAL_PUGIXML"] = True

        # OIIO CMake files are patched to check USE_* flags to require or not use dependencies
        tc.variables["USE_JPEGTURBO"] = (
            self.options.with_libjpeg == "libjpeg-turbo"
        )
        tc.variables[
            "USE_JPEG"
        ] = True  # Needed for jpeg.imageio plugin, libjpeg/libjpeg-turbo selection still works
        tc.variables["USE_HDF5"] = self.options.with_hdf5
        tc.variables["USE_OPENCOLORIO"] = self.options.with_opencolorio
        tc.variables["USE_OPENCV"] = self.options.with_opencv
        tc.variables["USE_TBB"] = self.options.with_tbb
        tc.variables["USE_DCMTK"] = self.options.with_dicom
        tc.variables["USE_FFMPEG"] = self.options.with_ffmpeg
        tc.variables["USE_FIELD3D"] = False
        tc.variables["USE_GIF"] = self.options.with_giflib
        tc.variables["USE_LIBHEIF"] = self.options.with_libheif
        tc.variables["USE_LIBRAW"] = self.options.with_raw
        tc.variables["USE_OPENVDB"] = self.options.with_openvdb
        tc.variables["USE_PTEX"] = self.options.with_ptex
        tc.variables["USE_R3DSDK"] = False
        tc.variables["USE_NUKE"] = False
        tc.variables["USE_OPENGL"] = False
        tc.variables["USE_QT"] = False
        tc.variables["USE_LIBPNG"] = self.options.with_libpng
        tc.variables["USE_FREETYPE"] = self.options.with_freetype
        tc.variables["USE_LIBWEBP"] = self.options.with_libwebp
        tc.variables["USE_OPENJPEG"] = self.options.with_openjpeg

        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    @staticmethod
    def _conan_comp(name):
        return f"openimageio_{name.lower()}"

    def _add_component(self, name):
        component = self.cpp_info.components[self._conan_comp(name)]
        component.set_property("cmake_target_name", f"OpenImageIO::{name}")
        component.names["cmake_find_package"] = name
        component.names["cmake_find_package_multi"] = name
        return component

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenImageIO")
        self.cpp_info.set_property("pkg_config_name", "OpenImageIO")

        self.cpp_info.names["cmake_find_package"] = "OpenImageIO"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenImageIO"
        self.cpp_info.names["pkg_config"] = "OpenImageIO"

        # OpenImageIO::OpenImageIO_Util
        OpenImageIOUtil = self._add_component("OpenImageIO_Util")
        OpenImageIOUtil.libs = ["OpenImageIO_Util"]
        OpenImageIOUtil.requires = [
            "boost::filesystem",
            "boost::thread",
            "boost::system",
            "boost::regex",
            "openexr::openexr",
        ]
        if self.settings.os in ["Linux", "FreeBSD"]:
            OpenImageIOUtil.system_libs.extend(
                ["dl", "m", "pthread"]
            )
        if self.options.with_tbb:
            OpenImageIOUtil.requires.append("onetbb::onetbb")

        # OpenImageIO::OpenImageIO
        OpenImageIO = self._add_component("OpenImageIO")
        OpenImageIO.libs = ["OpenImageIO"]
        OpenImageIO.requires = [
            "openimageio_openimageio_util",
            "zlib::zlib",
            "boost::thread",
            "boost::system",
            "boost::container",
            "boost::regex",
            "libtiff::libtiff",
            "openexr::openexr",
            "pugixml::pugixml",
            "tsl-robin-map::tsl-robin-map",
            "libsquish::libsquish",
            "fmt::fmt",
        ]

        if self.options.with_libjpeg == "libjpeg":
            OpenImageIO.requires.append("libjpeg::libjpeg")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            OpenImageIO.requires.append(
                "libjpeg-turbo::libjpeg-turbo"
            )
        if self.options.with_libpng:
            OpenImageIO.requires.append("libpng::libpng")
        if self.options.with_freetype:
            OpenImageIO.requires.append("freetype::freetype")
        if self.options.with_hdf5:
            OpenImageIO.requires.append("hdf5::hdf5")
        if self.options.with_opencolorio:
            OpenImageIO.requires.append("opencolorio::opencolorio")
        if self.options.with_opencv:
            OpenImageIO.requires.append("opencv::opencv")
        if self.options.with_dicom:
            OpenImageIO.requires.append("dcmtk::dcmtk")
        if self.options.with_ffmpeg:
            OpenImageIO.requires.append("ffmpeg::ffmpeg")
        if self.options.with_giflib:
            OpenImageIO.requires.append("giflib::giflib")
        if self.options.with_libheif:
            OpenImageIO.requires.append("libheif::libheif")
        if self.options.with_raw:
            OpenImageIO.requires.append("libraw::libraw")
        if self.options.with_openjpeg:
            OpenImageIO.requires.append("openjpeg::openjpeg")
        if self.options.with_openvdb:
            OpenImageIO.requires.append("openvdb::openvdb")
        if self.options.with_ptex:
            OpenImageIO.requires.append("ptex::ptex")
        if self.options.with_libwebp:
            OpenImageIO.requires.append("libwebp::libwebp")
        if self.settings.os in ["Linux", "FreeBSD"]:
            OpenImageIO.system_libs.extend(["dl", "m", "pthread"])

        if not self.options.shared:
            OpenImageIO.defines.append("OIIO_STATIC_DEFINE")
