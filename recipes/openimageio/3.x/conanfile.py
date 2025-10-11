from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.0.0"


class OpenImageIOConan(ConanFile):
    name = "openimageio"
    description = (
        "OpenImageIO is a library for reading and writing images, and a bunch "
        "of related classes, utilities, and applications. There is a "
        "particular emphasis on formats and functionality used in "
        "professional, large-scale animation and visual effects work for film."
    )
    topics = ("vfx", "image", "picture")
    license = "Apache-2.0", "BSD-3-Clause"
    homepage = "http://www.openimageio.org/"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_dicom": [True, False],
        "with_ffmpeg": [True, False],
        "with_freetype": [True, False],
        "with_giflib": [True, False],
        "with_hdf5": [True, False],
        "with_libheif": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo"],
        "with_libjxl": [True, False],
        "with_libpng": [True, False],
        "with_libultrahdr": [True, False],
        "with_libwebp": [True, False],
        "with_opencv": [True, False],
        "with_openjpeg": [True, False],
        "with_openvdb": [True, False],
        "with_ptex": [True, False],
        "with_raw": [True, False],
        "with_tbb": [True, False],

        # To be replaced with some proper check or fix of the build?
        # https://github.com/conan-io/conan-center-index/issues/23421
        "cci_hack": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_dicom": False,  # Heavy dependency, disabled by default
        "with_ffmpeg": True,
        "with_freetype": True,
        "with_giflib": True,
        "with_hdf5": True,
        "with_libheif": True,
        "with_libjpeg": "libjpeg",
        "with_libjxl": True,
        "with_libpng": True,
        "with_libultrahdr": True,
        "with_libwebp": True,
        "with_openjpeg": True,
        "with_openvdb": True,
        "with_opencv": False,
        "with_ptex": True,
        "with_raw": False,  # libraw is available under CDDL-1.0 or LGPL-2.1, for this reason it is disabled by default
        "with_tbb": True,

        "cci_hack": True,
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
        self.requires("libtiff/4.7.1")
        self.requires("imath/[>=3.1.9 <4]", transitive_headers=True)
        self.requires("openexr/3.3.5")
        self.requires("openjph/[>=0.23.1 <1]")
        if self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/[>=3.0.3 <4]")
        self.requires("pugixml/1.15")
        self.requires("tsl-robin-map/1.4.0")
        self.requires("fmt/11.2.0", transitive_headers=True)
        self.requires("opencolorio/2.5.0")

        # Workaround to be removed:
        # (libjxl requires lcms/2.16 and opencolorio has lcms/[>=2.16 <3])
        self.requires("lcms/2.16", override=True)

        # Optional libraries
        if self.options.with_libjxl:
            self.requires("libjxl/0.11.1")
        if self.options.with_libpng:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_freetype:
            self.requires("freetype/2.13.2")
        if self.options.with_hdf5:
            self.requires("hdf5/1.14.6")
        if self.options.with_opencv:
            self.requires("opencv/4.12.0")
        if self.options.with_tbb:
            self.requires("onetbb/2021.10.0")
        if self.options.with_dicom:
            self.requires("dcmtk/3.6.9")
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/7.1.1")
        # TODO: Field3D dependency
        if self.options.with_giflib:
            self.requires("giflib/5.2.2")
        if self.options.with_libheif:
            self.requires("libheif/1.20.1")
        if self.options.with_raw:
            self.requires("libraw/0.21.4")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.2")
        if self.options.with_openvdb:
            self.requires("openvdb/12.1.1")
        if self.options.with_ptex:
            self.requires("ptex/2.4.2")
        if self.options.with_libwebp:
            self.requires("libwebp/1.5.0")
        if self.options.with_libultrahdr:
            self.requires("libultrahdr/1.4.0")

        # TODO: R3DSDK dependency
        # TODO: Nuke dependency

    def build_requirements(self):
        # A minimum cmake version is now required that is reasonably new
        self.build_requires("cmake/[>=3.18.2 <5]")

    def validate(self):
        check_min_cppstd(self, 17)

        if is_msvc(self) and is_msvc_static_runtime(self) and self.options.shared:
            raise ConanInvalidConfiguration(
                "Building shared library with static runtime is not supported!"
            )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)

        # CMake options
        tc.cache_variables["CMAKE_DEBUG_POSTFIX"] = ""  # Needed for 2.3.x.x+ versions
        tc.cache_variables["OIIO_BUILD_TOOLS"] = True
        tc.cache_variables["OIIO_BUILD_TESTS"] = False
        tc.cache_variables["BUILD_DOCS"] = False
        tc.cache_variables["INSTALL_DOCS"] = False
        tc.cache_variables["INSTALL_FONTS"] = False
        tc.cache_variables["INSTALL_CMAKE_HELPER"] = False
        tc.cache_variables["EMBEDPLUGINS"] = True
        tc.cache_variables["USE_EXTERNAL_PUGIXML"] = True
        tc.cache_variables["BUILD_MISSING_FMT"] = False

        # Conan is normally not used for testing, so fixing this option to not build the tests
        tc.cache_variables["BUILD_TESTING"] = False

        tc.cache_variables["USE_DCMTK"] = self.options.with_dicom
        tc.cache_variables["USE_FFMPEG"] = self.options.with_ffmpeg
        tc.cache_variables["USE_FIELD3D"] = False
        tc.cache_variables["USE_FREETYPE"] = self.options.with_freetype
        tc.cache_variables["USE_GIF"] = self.options.with_giflib
        tc.cache_variables["USE_HDF5"] = self.options.with_hdf5
        # Needed for jpeg.imageio plugin, libjpeg/libjpeg-turbo selection still works
        tc.cache_variables["USE_JPEG"] = True
        # OIIO CMake files are patched to check USE_* flags to require or not use dependencies
        tc.cache_variables["USE_JPEGTURBO"] = (self.options.with_libjpeg == "libjpeg-turbo")
        tc.cache_variables["USE_LIBHEIF"] = self.options.with_libheif
        tc.cache_variables["USE_LIBJXL"] = self.options.with_libjxl
        tc.cache_variables["USE_LIBPNG"] = self.options.with_libpng
        tc.cache_variables["USE_LIBRAW"] = self.options.with_raw
        tc.cache_variables["USE_LIBWEBP"] = self.options.with_libwebp
        tc.cache_variables["USE_OPENCV"] = self.options.with_opencv
        tc.cache_variables["USE_OPENGL"] = False
        tc.cache_variables["USE_OPENJPEG"] = self.options.with_openjpeg
        tc.cache_variables["USE_OPENVDB"] = self.options.with_openvdb
        tc.cache_variables["USE_PTEX"] = self.options.with_ptex
        tc.cache_variables["USE_PYTHON"] = False
        tc.cache_variables["USE_QT"] = False
        tc.cache_variables["USE_TBB"] = self.options.with_tbb

        # Unsupported options
        tc.cache_variables["USE_NUKE"] = False
        tc.cache_variables["USE_R3DSDK"] = False

        # Override variable for internal linking visibility of Imath otherwise not visible
        # in the tools included in the build that consume the library. Also it is part of central
        # headers which is also why it is transitive_headers=True.
        tc.cache_variables["OPENIMAGEIO_IMATH_DEPENDENCY_VISIBILITY"] = "PUBLIC"

        if self.settings.os == "Linux":
            # Workaround for: https://github.com/conan-io/conan/issues/13560
            libdirs_host = [l for dependency in self.dependencies.host.values() for l in dependency.cpp_info.aggregated_components().libdirs]
            tc.variables["CMAKE_BUILD_RPATH"] = ";".join(libdirs_host)

        tc.generate()

        deps = CMakeDeps(self)
        # Map the name of openexr for the target name expected in OIIO cmake
        deps.set_property("openexr", "cmake_target_name", "OpenEXR::OpenEXR")
        if self.options.with_libultrahdr:
            deps.set_property("libultrahdr", "cmake_file_name", "libuhdr")
            deps.set_property("libultrahdr", "cmake_target_name", "libuhdr::libuhdr")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.os == "Windows":
            for vc_file in ("concrt", "msvcp", "vcruntime"):
                rm(self, f"{vc_file}*.dll", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    @staticmethod
    def _conan_comp(name):
        return f"openimageio_{name.lower()}"

    def _add_component(self, name):
        component = self.cpp_info.components[self._conan_comp(name)]
        component.set_property("cmake_target_name", f"OpenImageIO::{name}")
        return component

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenImageIO")
        self.cpp_info.set_property("pkg_config_name", "OpenImageIO")

        # OpenImageIO::OpenImageIO_Util
        open_image_io_util = self._add_component("OpenImageIO_Util")
        open_image_io_util.libs = ["OpenImageIO_Util"]
        open_image_io_util.requires = [
            "imath::imath",
            "openexr::openexr",
        ]
        if self.settings.os in ["Linux", "FreeBSD"]:
            open_image_io_util.system_libs.extend(
                ["dl", "m", "pthread"]
            )
        if self.options.with_tbb:
            open_image_io_util.requires.append("onetbb::onetbb")

        # OpenImageIO::OpenImageIO
        open_image_io = self._add_component("OpenImageIO")
        open_image_io.libs = ["OpenImageIO"]
        open_image_io.requires = [
            "openimageio_openimageio_util",
            "zlib::zlib",
            "libtiff::libtiff",
            "pugixml::pugixml",
            "tsl-robin-map::tsl-robin-map",
            "fmt::fmt",
            "imath::imath",
            "openexr::openexr",
            "opencolorio::opencolorio",
            "openjph::openjph",
        ]

        if self.options.with_libjxl:
            open_image_io.requires += ["libjxl::libjxl", "libjxl::jxl_cms"]
        if self.options.with_libjpeg == "libjpeg":
            open_image_io.requires.append("libjpeg::libjpeg")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            open_image_io.requires.append(
                "libjpeg-turbo::libjpeg-turbo"
            )
        if self.options.with_libpng:
            open_image_io.requires.append("libpng::libpng")
        if self.options.with_freetype:
            open_image_io.requires.append("freetype::freetype")
        if self.options.with_hdf5:
            open_image_io.requires.append("hdf5::hdf5")
        if self.options.with_opencv:
            open_image_io.requires.append("opencv::opencv")
        if self.options.with_dicom:
            open_image_io.requires.append("dcmtk::dcmtk")
        if self.options.with_ffmpeg:
            open_image_io.requires.append("ffmpeg::ffmpeg")
        if self.options.with_giflib:
            open_image_io.requires.append("giflib::giflib")
        if self.options.with_libheif:
            open_image_io.requires.append("libheif::libheif")
        if self.options.with_raw:
            open_image_io.requires.append("libraw::libraw")
        if self.options.with_openjpeg:
            open_image_io.requires.append("openjpeg::openjpeg")
        if self.options.with_openvdb:
            open_image_io.requires.append("openvdb::openvdb")
        if self.options.with_ptex:
            open_image_io.requires.append("ptex::ptex")
        if self.options.with_libwebp:
            open_image_io.requires.append("libwebp::libwebp")
        if self.options.with_libultrahdr:
            open_image_io.requires.append("libultrahdr::libultrahdr")
        if self.settings.os in ["Linux", "FreeBSD"]:
            open_image_io.system_libs.extend(["dl", "m", "pthread"])

        if not self.options.shared:
            open_image_io.defines.append("OIIO_STATIC_DEFINE")
