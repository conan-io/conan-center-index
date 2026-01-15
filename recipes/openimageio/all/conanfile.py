from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.0"


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
        "with_libjpeg": ["libjpeg", "libjpeg-turbo"],
        "with_libjxl": [True, False],
        "with_libpng": [True, False],
        "with_freetype": [True, False],
        "with_opencolorio": [True, False],
        "with_opencv": [True, False],
        "with_tbb": [True, False],
        "with_dicom": [True, False],
        "with_ffmpeg": [True, False],
        "with_giflib": [True, False],
        "with_libheif": [True, False],
        "with_raw": [True, False],
        "with_openjpeg": [True, False],
        "with_openjph": [True, False],
        "with_openvdb": [True, False],
        "with_ptex": [True, False],
        "with_libwebp": [True, False],
        "with_libultrahdr": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libjpeg": "libjpeg",
        "with_libjxl": True,
        "with_libpng": True,
        "with_freetype": True,
        "with_opencolorio": True,
        "with_opencv": False,
        "with_tbb": False,
        "with_dicom": False,  # Heavy dependency, disabled by default
        "with_ffmpeg": True,
        "with_giflib": True,
        "with_libheif": True,
        "with_raw": False,  # libraw is available under CDDL-1.0 or LGPL-2.1, for this reason it is disabled by default
        "with_openjpeg": True,
        "with_openjph": True,
        "with_openvdb": False,  # FIXME: broken on M1
        "with_ptex": True,
        "with_libwebp": True,
        "with_libultrahdr": True
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "3.0":
            del self.options.with_libultrahdr
            del self.options.with_libjxl
            del self.options.with_openjph
        if Version(self.version) >= "3.0":
            # OpenColorIO became mandatory with OpenImageIO 3.0 so is no longer an option
            del self.options.with_opencolorio

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        # Required libraries
        self.requires("zlib/[>=1.2.11 <2]")
        if Version(self.version) < "3.0":
            self.requires("boost/1.84.0")
        self.requires("libtiff/[>=4.6.0 <5]")
        self.requires("imath/[>3.1.9 <4]", transitive_headers=True)
        self.requires("openexr/[>=3.2.3 <4]")
        if self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/[>=9f]")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/[>=3.0.2 <4]")
        if self.options.get_safe("with_libjxl"):
            self.requires("libjxl/0.11.1")
        self.requires("pugixml/1.14")
        self.requires("libsquish/1.15")
        self.requires("tsl-robin-map/1.2.1")
        self.requires("fmt/10.2.1", transitive_headers=True)

        # Optional libraries
        if self.options.with_libpng:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_freetype:
            self.requires("freetype/2.13.2")
        if self.options.get_safe("with_opencolorio", True):
            self.requires("opencolorio/[>=2.3.1 <4]")
        if self.options.with_opencv:
            self.requires("opencv/[>=4.8.1 <5]")
        if self.options.with_tbb:
            self.requires("onetbb/2021.10.0")
        if self.options.with_dicom:
            self.requires("dcmtk/3.6.7")
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/[>=6.1 <8.0]")
        # TODO: Field3D dependency
        if self.options.with_giflib:
            self.requires("giflib/5.2.1")
        if self.options.with_libheif:
            self.requires("libheif/[>=1.16.2 <2]")
        if self.options.with_raw:
            self.requires("libraw/0.21.2")
        if self.options.with_openjpeg:
            self.requires("openjpeg/[>=2.5.2 <3]")
        if self.options.get_safe("with_openjph", False):
            self.requires("openjph/[>=0.16.0 <1]")
        if self.options.with_openvdb:
            self.requires("openvdb/8.0.1")
        if self.options.with_ptex:
            self.requires("ptex/2.4.2")
        if self.options.with_libwebp:
            self.requires("libwebp/[>=1.3.2 <2]")
        if self.options.get_safe("with_libultrahdr"):
            self.requires("libultrahdr/1.4.0")
        # TODO: R3DSDK dependency
        # TODO: Nuke dependency
        self.tool_requires("cmake/[>=3.18]")

    def validate(self):
        check_min_cppstd(self, 14 if Version(self.version) < "3.0" else 17)
        if is_msvc(self) and is_msvc_static_runtime(self) and self.options.shared:
            raise ConanInvalidConfiguration(
                "Building shared library with static runtime is not supported!"
            )

        if self.options.get_safe("with_openjph", False) and not self.options.with_openjpeg:
            raise ConanInvalidConfiguration(
                "openjph (with_openjph) can only be used when the JPEG 2000 module is build which requires openjpeg(with_openjpeg=True)"
            )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

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
        tc.variables["BUILD_MISSING_FMT"] = False

        # Conan is normally not used for testing, so fixing this option to not build the tests
        tc.variables["BUILD_TESTING"] = False

        # OIIO CMake files are patched to check USE_* flags to require or not use dependencies
        tc.variables["USE_JPEGTURBO"] = (
            self.options.with_libjpeg == "libjpeg-turbo"
        )
        tc.variables[
            "USE_JPEG"
        ] = True  # Needed for jpeg.imageio plugin, libjpeg/libjpeg-turbo selection still works
        tc.cache_variables["USE_JXL"] = self.options.get_safe("with_libjxl", False)
        tc.variables["USE_OPENCOLORIO"] = self.options.get_safe("with_opencolorio", True)
        tc.variables["USE_OPENCV"] = self.options.with_opencv
        tc.variables["USE_TBB"] = self.options.with_tbb
        tc.variables["USE_DCMTK"] = self.options.with_dicom
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
        tc.cache_variables["USE_OPENJPH"] = self.options.get_safe("with_openjph", False)

        tc.cache_variables["USE_FFMPEG"] = self.options.with_ffmpeg
        if self.options.with_ffmpeg:
            tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_FFmpeg"] = True
            tc.cache_variables["FFMPEG_VERSION"] = f'"{str(self.dependencies["ffmpeg"].ref.version)}"'

        if Version(self.version) < "3.0":
            tc.cache_variables["Boost_USE_STATIC_LIBS"] = not self.dependencies["boost"].options.shared

        tc.cache_variables["BUILD_MISSING_ROBINMAP"] = False
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_Robinmap"] = True
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_pugixml"] = True
        if Version(self.version) < "3.0":
            tc.cache_variables["INTERNALIZE_FMT"] = False
        else: # Variable renamed with 3.0
            tc.cache_variables["OIIO_INTERNALIZE_FMT"] = False
        tc.cache_variables["ROBINMAP_INCLUDES"] = self.dependencies["tsl-robin-map"].cpp_info.includedirs[0].replace("\\", "/")
        tc.cache_variables["IMATH_INCLUDES"] = self.dependencies["imath"].cpp_info.includedirs[0].replace("\\", "/")
        tc.cache_variables["OPENEXR_INCLUDES"] = self.dependencies["openexr"].cpp_info.includedirs[0].replace("\\", "/")
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_PNG"] = self.options.with_libpng
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_Freetype"] = self.options.with_freetype
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_OpenColorIO"] = self.options.get_safe("with_opencolorio", True)
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_OpenCV"] = self.options.with_opencv
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_TBB"] = self.options.with_tbb
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_DCMTK"] = self.options.with_dicom
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_GIF"] = self.options.with_giflib
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_Libheif"] = self.options.with_libheif
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_LibRaw"] = self.options.with_raw
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_OpenJPEG"] = self.options.with_openjpeg
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_openjph"] = self.options.get_safe("with_openjph", False)
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_Ptex"] = self.options.with_ptex
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_WebP"] = self.options.with_libwebp
        tc.cache_variables["CMAKE_REQUIRE_FIND_PACKAGE_JXL"] = self.options.get_safe("with_libjxl", False)

        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_libjpeg-turbo"] = self.options.with_libjpeg != "libjpeg-turbo"
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_R3DSDK"] = True
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_Nuke"] = True
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_JXL"] = not self.options.get_safe("with_libjxl", False)


        if self.settings.os == "Linux":
            # Workaround for: https://github.com/conan-io/conan/issues/13560
            # note: should not be needed if CMakeConfigDeps is used
            libdirs_host = [l for dependency in self.dependencies.host.values() for l in dependency.cpp_info.aggregated_components().libdirs]
            tc.cache_variables["CMAKE_BUILD_RPATH"] = ";".join(libdirs_host)
        tc.generate()
        deps = CMakeDeps(self)
        deps.set_property("fmt", "cmake_additional_variables_prefixes", ["FMT"])
        deps.set_property("ffmpeg", "cmake_additional_variables_prefixes", ["FFMPEG"])
        deps.set_property("ffmpeg", "cmake_file_name", "FFmpeg")
        deps.set_property("libheif", "cmake_additional_variables_prefixes", ["LIBHEIF"])
        deps.set_property("tsl-robin-map", "cmake_file_name", "Robinmap")
        deps.set_property("tsl-robin-map", "cmake_additional_variables_prefixes", ["ROBINMAP"])
        if Version(self.version) >= "3.0":
            deps.set_property("openexr", "cmake_target_name", "OpenEXR::OpenEXR")
            deps.set_property("libultrahdr", "cmake_file_name", "libuhdr")
            deps.set_property("libultrahdr", "cmake_target_name", "libuhdr::libuhdr")
            deps.set_property("libjxl", "cmake_file_name", "JXL")
            deps.set_property("openjph", "cmake_target_name", "openjph")
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
        component.names["cmake_find_package"] = name
        component.names["cmake_find_package_multi"] = name
        return component

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenImageIO")
        self.cpp_info.set_property("pkg_config_name", "OpenImageIO")

        # OpenImageIO::OpenImageIO_Util
        open_image_io_util = self._add_component("OpenImageIO_Util")
        open_image_io_util.libs = ["OpenImageIO_Util"]
        boost_deps = ["boost::filesystem", "boost::thread", "boost::system", "boost::regex"]
        open_image_io_util.requires = [
            *(boost_deps if Version(self.version) < "3.0" else []),
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
            *(boost_deps if Version(self.version) < "3.0" else []),
            "libtiff::libtiff",
            "pugixml::pugixml",
            "tsl-robin-map::tsl-robin-map",
            "libsquish::libsquish",
            "fmt::fmt",
            "imath::imath",
            "openexr::openexr",
        ]

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
        if self.options.get_safe("with_opencolorio", True):
            open_image_io.requires.append("opencolorio::opencolorio")
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
        if self.options.get_safe("with_openjph", False):
            open_image_io.requires.append("openjph::openjph")
        if self.options.with_openvdb:
            open_image_io.requires.append("openvdb::openvdb")
        if self.options.with_ptex:
            open_image_io.requires.append("ptex::ptex")
        if self.options.with_libwebp:
            open_image_io.requires.append("libwebp::libwebp")
        if self.options.get_safe("with_libultrahdr"):
            open_image_io.requires.append("libultrahdr::libultrahdr")
        if self.options.get_safe("with_libjxl"):
            open_image_io.requires.extend(["libjxl::libjxl", "libjxl::jxl_threads"])
        if self.settings.os in ["Linux", "FreeBSD"]:
            open_image_io.system_libs.extend(["dl", "m", "pthread"])
        if not self.options.shared:
            open_image_io.defines.append("OIIO_STATIC_DEFINE")
