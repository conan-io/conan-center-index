from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os
import glob

required_conan_version = ">=1.33.0"


class ImageMagicConan(ConanFile):
    name = "imagemagick"
    description = (
        "ImageMagick is a free and open-source software suite for displaying, converting, and editing "
        "raster image and vector image files"
    )
    topics = ("imagemagick", "images", "manipulating")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://imagemagick.org"
    license = "ImageMagick"
    settings = "os", "arch", "compiler", "build_type"
    generators = "pkg_config", "cmake", "cmake_find_package"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "hdri": [True, False],
        "quantum_depth": [8, 16, 32],
        "with_zlib": [True, False],
        "with_bzlib": [True, False],
        "with_zstd": [True, False],
        "with_lzma": [True, False],
        "with_lcms": [True, False],
        "with_openexr": [True, False],
        "with_heic": [True, False],
        "with_jbig": [True, False],
        "with_jpeg": [None, "libjpeg", "libjpeg-turbo"],
        "with_jxl": [True, False],
        "with_openjp2": [True, False],
        "with_pango": [True, False],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_webp": [True, False],
        "with_xml2": [True, False],
        "with_freetype": [True, False],
        "with_djvu": [True, False],
        "with_raw": [True, False],
        "with_openmp": [True, False],
        "with_threads": [True, False],
        "magickpp": [True, False],
        "utilities": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "hdri": True,
        "quantum_depth": 16,
        "with_zlib": True,
        "with_bzlib": True,
        "with_zstd": False,
        "with_lzma": True,
        "with_lcms": True,
        "with_openexr": True,
        "with_heic": True,
        "with_jbig": True,
        "with_jpeg": "libjpeg",
        "with_jxl": False,
        "with_openjp2": True,
        "with_pango": True,
        "with_png": True,
        "with_tiff": True,
        "with_webp": False,
        "with_xml2": True,
        "with_freetype": True,
        "with_djvu": False,
        "with_raw": False,
        "with_openmp": True,
        "with_threads": True,
        "magickpp": True,
        "utilities": True,
    }
    exports_sources = "patches/*"

    _cmake = None

    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "ImageMagick"

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self, generator="Ninja")

        self._cmake.definitions["MAGICK_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["MAGICK_HDRI_ENABLE"] = self.options.hdri
        self._cmake.definitions["MAGICKCORE_QUANTUM_DEPTH"] = self.options.quantum_depth
        self._cmake.definitions["BUILD_MAGICKPP"] = self.options.magickpp
        self._cmake.definitions["BUILD_UTILITIES"] = self.options.utilities
        self._cmake.definitions["OPENMP_SUPPORT"] = self.options.with_openmp
        self._cmake.definitions["THREADS_SUPPORT"] = self.options.with_threads

        self._cmake.definitions["BZLIB_DELEGATE"] = self.options.with_bzlib
        self._cmake.definitions["LZMA_DELEGATE"] = self.options.with_lzma
        self._cmake.definitions["ZLIB_DELEGATE"] = self.options.with_zlib
        self._cmake.definitions["ZSTD_DELEGATE"] = self.options.with_zstd
        self._cmake.definitions["LCMS_DELEGATE"] = self.options.with_lcms
        self._cmake.definitions["FREETYPE_DELEGATE"] = self.options.with_freetype
        self._cmake.definitions["XML_DELEGATE"] = self.options.with_xml2
        self._cmake.definitions["TIFF_DELEGATE"] = self.options.with_tiff
        self._cmake.definitions["HEIC_DELEGATE"] = self.options.with_heic
        self._cmake.definitions["JBIG_DELEGATE"] = self.options.with_jbig
        self._cmake.definitions["JPEG_DELEGATE"] = self.options.with_jpeg
        self._cmake.definitions["LIBOPENJP2_DELEGATE"] = self.options.with_openjp2
        self._cmake.definitions["OPENEXR_DELEGATE"] = self.options.with_openexr
        self._cmake.definitions["PNG_DELEGATE"] = self.options.with_png
        self._cmake.definitions["RAW_R_DELEGATE"] = self.options.with_raw
        self._cmake.definitions["WEBP_DELEGATE"] = self.options.with_webp
        self._cmake.definitions["JXL_DELEGATE"] = self.options.with_jxl

        self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def _libname(self, library):
        suffix = "HDRI" if self.options.hdri else ""
        return "%s-%s.Q%s%s" % (
            library,
            tools.Version(self.version).major,
            self.options.quantum_depth,
            suffix,
        )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.with_bzlib:
            self.requires("bzip2/1.0.8")
        if self.options.with_zstd:
            self.requires("zstd/1.5.2")
        if self.options.with_lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.with_lcms:
            self.requires("lcms/2.13.1")
        if self.options.with_openexr:
            self.requires("openexr/2.5.7")
        if self.options.with_heic:
            self.requires("libheif/1.12.0")
        if self.options.with_jbig:
            self.requires("jbig/20160605")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9d")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.2")
        if self.options.with_jxl:
            self.requires("libjxl/0.6.1")
        if self.options.with_openjp2:
            self.requires("openjpeg/2.5.0")
        if self.options.with_pango:
            self.requires("pango/1.48.5")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_tiff:
            self.requires("libtiff/4.3.0")
        if self.options.with_webp:
            self.requires("libwebp/1.2.2")
        if self.options.with_xml2:
            self.requires("libxml2/2.9.12")
        if self.options.with_freetype:
            self.requires("freetype/2.10.4")
        if self.options.with_raw:
            self.requires("libraw/0.20.2")
        if self.options.with_djvu:
            self.output.warn("Conan package for djvu is not available, this package will be used from system.")
        if self.options.with_openmp:
            self.output.warn("Conan package for OpenMP is not available, this package will be used from system.")

    def build_requirements(self):
        self.build_requires("cmake/3.22.0")
        self.build_requires("ninja/1.10.2")
        self.build_requires("pkgconf/1.7.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version]["source"], destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, {}):
            tools.patch(**patch)

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                "magick_check_env()",
                "include(${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake)\n"
                "conan_basic_setup(KEEP_RPATHS)\n"
                "magick_check_env()")

        with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
            cmake = self._configure_cmake()
            with tools.run_environment(self):
                cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install(build_dir=self._build_subfolder)

    def package_info(self):
        # FIXME model official FindImageMagick https://cmake.org/cmake/help/latest/module/FindImageMagick.html
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        core_requires = []
        if self.options.with_zlib:
            core_requires.append("zlib::zlib")
        if self.options.with_bzlib:
            core_requires.append("bzip2::bzip2")
        if self.options.with_zstd:
            core_requires.append("zstd::zstd")
        if self.options.with_lzma:
            core_requires.append("xz_utils::xz_utils")
        if self.options.with_lcms:
            core_requires.append("lcms::lcms")
        if self.options.with_openexr:
            core_requires.append("openexr::openexr")
        if self.options.with_heic:
            core_requires.append("libheif::libheif")
        if self.options.with_jbig:
            core_requires.append("jbig::jbig")
        if self.options.with_jpeg:
            core_requires.append("{0}::{0}".format(self.options.with_jpeg))
        if self.options.with_jxl:
            core_requires.append("libjxl::libjxl")
        if self.options.with_openjp2:
            core_requires.append("openjpeg::openjpeg")
        if self.options.with_pango:
            core_requires.append("pango::pango")
        if self.options.with_png:
            core_requires.append("libpng::libpng")
        if self.options.with_tiff:
            core_requires.append("libtiff::libtiff")
        if self.options.with_webp:
            core_requires.append("libwebp::libwebp")
        if self.options.with_xml2:
            core_requires.append("libxml2::libxml2")
        if self.options.with_freetype:
            core_requires.append("freetype::freetype")
        if self.options.with_raw:
            core_requires.append("libraw::libraw")

        if self.settings.os == "Linux":
            self.cpp_info.components["MagickCore"].system_libs.append("pthread")

        self.cpp_info.components["MagickCore"].defines.append(
            "MAGICKCORE_QUANTUM_DEPTH=%s" % self.options.quantum_depth
        )
        self.cpp_info.components["MagickCore"].defines.append(
            "MAGICKCORE_HDRI_ENABLE=%s" % int(bool(self.options.hdri))
        )
        self.cpp_info.components["MagickCore"].defines.append(
            "_MAGICKDLL_=1" if self.options.shared else "_MAGICKLIB_=1"
        )

        imagemagick_include_dir = (
            "include/ImageMagick-%s" % tools.Version(self.version).major
        )

        self.cpp_info.components["MagickCore"].includedirs = [imagemagick_include_dir]
        self.cpp_info.components["MagickCore"].libs.append(self._libname("MagickCore"))
        self.cpp_info.components["MagickCore"].requires = core_requires
        self.cpp_info.components["MagickCore"].names["pkg_config"] = ["MagicCore"]

        self.cpp_info.components[self._libname("MagickCore")].requires = ["MagickCore"]
        self.cpp_info.components[self._libname("MagickCore")].names["pkg_config"] = [
            self._libname("MagickCore")
        ]

        if not self.options.shared and self.options.with_openmp:
            openmp_flags = []
            if self.settings.compiler in ("Visual Studio", "msvc"):
                openmp_flags = ["-openmp"]
            elif self.settings.compiler in ("gcc", "clang"):
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler == "apple-clang":
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]

            self.cpp_info.components["MagickCore"].sharedlinkflags = openmp_flags
            self.cpp_info.components["MagickCore"].exelinkflags = openmp_flags

        self.cpp_info.components["MagickWand"].includedirs = [
            imagemagick_include_dir + "/MagickWand"
        ]
        self.cpp_info.components["MagickWand"].libs = [self._libname("MagickWand")]
        self.cpp_info.components["MagickWand"].requires = ["MagickCore"]
        self.cpp_info.components["MagickWand"].names["pkg_config"] = ["MagickWand"]

        self.cpp_info.components[self._libname("MagickWand")].requires = ["MagickWand"]
        self.cpp_info.components[self._libname("MagickWand")].names[
            "pkg_config"
        ] = self._libname("MagickWand")

        if self.options.magickpp:
            self.cpp_info.components["Magick++"].includedirs = [
                imagemagick_include_dir + "/Magick++"
            ]
            self.cpp_info.components["Magick++"].libs = [self._libname("Magick++")]
            self.cpp_info.components["Magick++"].requires = ["MagickWand"]
            self.cpp_info.components["Magick++"].names["pkg_config"] = [
                "Magick++",
                self._libname("Magick++"),
            ]

            self.cpp_info.components[self._libname("Magick++")].requires = ["Magick++"]
            self.cpp_info.components[self._libname("Magick++")].names[
                "pkg_config"
            ] = self._libname("Magick++")

            if not self.options.shared:
                self.cpp_info.components["MagickCore"].defines.append("STATIC_MAGICK=1")
                self.cpp_info.components["MagickCore"].defines.append("NOAUTOLINK_MAGICK=1")
