import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=2.4"


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
        "with_lcms": [True, False],
        "with_openexr": [True, False],
        "with_heic": [True, False],
        "with_jpeg": ["libjpeg", "libjpeg-turbo"],
        "with_openjp2": [True, False],
        "with_pango": [True, False],
        "with_tiff": [True, False],
        "with_webp": [True, False],
        "with_xml2": [True, False],
        "with_freetype": [True, False],
        "utilities": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "hdri": True,
        "quantum_depth": 16,
        "with_lcms": True,
        "with_openexr": True,
        "with_heic": True,
        "with_jpeg": "libjpeg",
        "with_openjp2": True,
        "with_pango": True,
        "with_tiff": True,
        "with_webp": False,
        "with_xml2": True,
        "with_freetype": True,
        "utilities": True,
    }
    implements = ["auto_shared_fpic"]

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "Windows builds of ImageMagick require MFC which cannot currently be sourced from CCI."
            )

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Always required: foundational compression/format libraries with no real
        # reason for a consumer to want them disabled.
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("bzip2/1.0.8")
        self.requires("xz_utils/[>=5.4.5 <6]")
        self.requires("libpng/[>=1.6 <2]")
        if self.options.with_lcms:
            self.requires("lcms/[>=2.16 <3]")
        if self.options.with_openexr:
            self.requires("openexr/[>=3.2.3 <4]")
        if self.options.with_heic:
            self.requires("libheif/[>=1.16 <2]")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/[>=9e]")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/[>=3 <4]")
        if self.options.with_openjp2:
            self.requires("openjpeg/[>=2.5.2 <3]")
        if self.options.with_pango:
            self.requires("pango/[>=1.50.7 <2]")
        if self.options.with_tiff:
            self.requires("libtiff/[>=4.6.0 <5]")
        if self.options.with_webp:
            self.requires("libwebp/[>=1.3 <2]")
        if self.options.with_xml2:
            self.requires("libxml2/[>=2.12.5 <3]")
        if self.options.with_freetype:
            self.requires("freetype/[>=2.13 <3]")
            # fontconfig only feeds discovered font paths to freetype for rasterization,
            # so it is pointless without it. Already pulled in transitively by pango on
            # most platforms, so this rarely adds a new dependency in practice.
            self.requires("fontconfig/[>=2.13.91 <3]")

    def build_requirements(self):
        self.tool_requires("pkgconf/[>=2.2 <3]")

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
            "--enable-hdri={}".format(yes_no(self.options.hdri)),
            "--with-quantum-depth={}".format(self.options.quantum_depth),
            "--with-zlib=yes",
            "--with-bzlib=yes",
            "--with-lzma=yes",
            "--with-png=yes",
            "--with-jpeg=yes",
            "--with-lcms={}".format(yes_no(self.options.with_lcms)),
            "--with-openexr={}".format(yes_no(self.options.with_openexr)),
            "--with-heic={}".format(yes_no(self.options.with_heic)),
            "--with-openjp2={}".format(yes_no(self.options.with_openjp2)),
            "--with-pango={}".format(yes_no(self.options.with_pango)),
            "--with-tiff={}".format(yes_no(self.options.with_tiff)),
            "--with-webp={}".format(yes_no(self.options.with_webp)),
            "--with-xml={}".format(yes_no(self.options.with_xml2)),
            "--with-freetype={}".format(yes_no(self.options.with_freetype)),
            "--with-fontconfig={}".format(yes_no(self.options.with_freetype)),
            "--with-utilities={}".format(yes_no(self.options.utilities)),
            # Not packaged by this recipe and auto-detected by default (--with-X=yes)
            # otherwise. Disable them explicitly so the build does not silently link
            # against whatever happens to be installed on the build machine.
            "--without-jbig",
            "--without-djvu",
            "--without-zip",
            "--without-zstd",
            "--without-raqm",
            "--without-gvc",
            "--without-dmr",
            "--without-jxl",
            "--without-lqr",
            "--without-raw",
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
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def _libname(self, library):
        suffix = "HDRI" if self.options.hdri else ""
        return "{}-{}.Q{}{}".format(library, Version(self.version).major, self.options.quantum_depth, suffix)

    def package_info(self):
        # FIXME model official FindImageMagick https://cmake.org/cmake/help/latest/module/FindImageMagick.html
        core_requires = ["zlib::zlib", "bzip2::bzip2", "xz_utils::xz_utils", "libpng::libpng"]
        core_requires.append("{0}::{0}".format(self.options.with_jpeg))
        if self.options.with_lcms:
            core_requires.append("lcms::lcms")
        if self.options.with_openexr:
            core_requires.append("openexr::openexr")
        if self.options.with_heic:
            core_requires.append("libheif::libheif")
        if self.options.with_openjp2:
            core_requires.append("openjpeg::openjpeg")
        if self.options.with_pango:
            core_requires.append("pango::pango")
        if self.options.with_tiff:
            core_requires.append("libtiff::libtiff")
        if self.options.with_webp:
            core_requires.append("libwebp::libwebp")
        if self.options.with_xml2:
            core_requires.append("libxml2::libxml2")
        if self.options.with_freetype:
            core_requires.append("freetype::freetype")
            core_requires.append("fontconfig::fontconfig")

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

        imagemagick_include_dir = "include/ImageMagick-%s" % Version(self.version).major

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
