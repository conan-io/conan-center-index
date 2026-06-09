import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=2.0"


class ImageMagicConan(ConanFile):
    name = "imagemagick"
    description = (
        "ImageMagick is a free and open-source software suite for displaying, converting, and editing "
        "raster image and vector image files"
    )
    topics = ("images", "manipulating")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://imagemagick.org"
    license = "ImageMagick"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "hdri": [True, False],
        "quantum_depth": [8, 16, 32],
        "with_zlib": [True, False],
        "with_bzlib": [True, False],
        "with_lzma": [True, False],
        "with_lcms": [True, False],
        "with_openexr": [True, False],
        "with_heic": [True, False],
        "with_jbig": [True, False],
        "with_jpeg": [None, "libjpeg", "libjpeg-turbo"],
        "with_openjp2": [True, False],
        "with_pango": [True, False],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_webp": [True, False],
        "with_xml2": [True, False],
        "with_freetype": [True, False],
        "with_djvu": [True, False],
        "utilities": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "hdri": True,
        "quantum_depth": 16,
        "with_zlib": True,
        "with_bzlib": True,
        "with_lzma": True,
        "with_lcms": True,
        "with_openexr": True,
        "with_heic": True,
        "with_jbig": True,
        "with_jpeg": "libjpeg",
        "with_openjp2": True,
        "with_pango": True,
        "with_png": True,
        "with_tiff": True,
        "with_webp": False,
        "with_xml2": True,
        "with_freetype": True,
        "with_djvu": False,
        "utilities": True,
    }

    @property
    def _major(self):
        return Version(self.version).major

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.3.2")
        if self.options.with_bzlib:
            self.requires("bzip2/1.0.8")
        if self.options.with_lzma:
            self.requires("xz_utils/5.8.3")
        if self.options.with_lcms:
            self.requires("lcms/2.17")
        if self.options.with_openexr:
            self.requires("openexr/3.4.12")
        if self.options.with_heic:
            self.requires("libheif/1.20.1")
        if self.options.with_jbig:
            self.requires("jbig/20160605")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9f")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.1.4.1")
        if self.options.with_openjp2:
            self.requires("openjpeg/2.5.4")
        if self.options.with_pango:
            self.requires("pango/1.57.0")
        if self.options.with_png:
            self.requires("libpng/1.6.58")
        if self.options.with_tiff:
            self.requires("libtiff/4.7.1")
        if self.options.with_webp:
            self.requires("libwebp/1.6.0")
        if self.options.with_xml2:
            self.requires("libxml2/2.15.3")
        if self.options.with_freetype:
            self.requires("freetype/2.14.3")
        if self.options.with_djvu:
            # FIXME: missing djvu recipe
            self.output.warning(
                "There is no djvu package available on Conan (yet). "
                "This recipe will use the one present on the system (if available)."
            )

    def build_requirements(self):
        self.tool_requires("pkgconf/2.2.0")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "Windows builds of ImageMagick require MFC which cannot currently be sourced from CCI."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        def yes_no(o):
            return "yes" if o else "no"

        tc = AutotoolsToolchain(self)
        tc.configure_args += [
            "--disable-openmp",
            "--disable-docs",
            "--with-perl=no",
            "--with-x=no",
            "--with-fontconfig=no",
            "--enable-hdri={}".format(yes_no(self.options.hdri)),
            "--with-quantum-depth={}".format(self.options.quantum_depth),
            "--with-zlib={}".format(yes_no(self.options.with_zlib)),
            "--with-bzlib={}".format(yes_no(self.options.with_bzlib)),
            "--with-lzma={}".format(yes_no(self.options.with_lzma)),
            "--with-lcms={}".format(yes_no(self.options.with_lcms)),
            "--with-openexr={}".format(yes_no(self.options.with_openexr)),
            "--with-heic={}".format(yes_no(self.options.with_heic)),
            "--with-jbig={}".format(yes_no(self.options.with_jbig)),
            "--with-jpeg={}".format(yes_no(self.options.with_jpeg)),
            "--with-openjp2={}".format(yes_no(self.options.with_openjp2)),
            "--with-pango={}".format(yes_no(self.options.with_pango)),
            "--with-png={}".format(yes_no(self.options.with_png)),
            "--with-tiff={}".format(yes_no(self.options.with_tiff)),
            "--with-webp={}".format(yes_no(self.options.with_webp)),
            "--with-xml={}".format(yes_no(self.options.with_xml2)),
            "--with-freetype={}".format(yes_no(self.options.with_freetype)),
            "--with-djvu={}".format(yes_no(self.options.with_djvu)),
            "--with-utilities={}".format(yes_no(self.options.utilities)),
        ]
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def _libname(self, library):
        suffix = "HDRI" if self.options.hdri else ""
        return "{}-{}.Q{}{}".format(library, self._major, self.options.quantum_depth, suffix)

    def package_info(self):
        # FIXME model official FindImageMagick https://cmake.org/cmake/help/latest/module/FindImageMagick.html
        core_requires = []
        if self.options.with_zlib:
            core_requires.append("zlib::zlib")
        if self.options.with_bzlib:
            core_requires.append("bzip2::bzip2")
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

        if self.settings.os in ("Linux", "FreeBSD"):
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

        imagemagick_include_dir = "include/ImageMagick-%s" % self._major

        self.cpp_info.components["MagickCore"].includedirs = [imagemagick_include_dir]
        self.cpp_info.components["MagickCore"].libs.append(self._libname("MagickCore"))
        self.cpp_info.components["MagickCore"].requires = core_requires
        self.cpp_info.components["MagickCore"].set_property("pkg_config_name", "MagickCore")
        self.cpp_info.components["MagickCore"].set_property(
            "pkg_config_aliases", [self._libname("MagickCore")]
        )

        self.cpp_info.components["MagickWand"].includedirs = [imagemagick_include_dir + "/MagickWand"]
        self.cpp_info.components["MagickWand"].libs = [self._libname("MagickWand")]
        self.cpp_info.components["MagickWand"].requires = ["MagickCore"]
        self.cpp_info.components["MagickWand"].set_property("pkg_config_name", "MagickWand")
        self.cpp_info.components["MagickWand"].set_property(
            "pkg_config_aliases", [self._libname("MagickWand")]
        )

        self.cpp_info.components["Magick++"].includedirs = [imagemagick_include_dir + "/Magick++"]
        self.cpp_info.components["Magick++"].libs = [self._libname("Magick++")]
        self.cpp_info.components["Magick++"].requires = ["MagickWand"]
        self.cpp_info.components["Magick++"].set_property("pkg_config_name", "Magick++")
        self.cpp_info.components["Magick++"].set_property(
            "pkg_config_aliases", [self._libname("Magick++")]
        )
