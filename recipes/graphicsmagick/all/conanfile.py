import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import stdcpp_library
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout

required_conan_version = ">=2.4"


class GraphicsMagickConan(ConanFile):
    name = "graphicsmagick"
    description = (
        "GraphicsMagick is the swiss army knife of image processing: a robust, efficient collection of "
        "tools and libraries to read, write, and manipulate images in over 88 major formats"
    )
    topics = ("images", "manipulating", "image-processing")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.graphicsmagick.org"
    license = "MIT"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "quantum_depth": [8, 16, 32],
        "with_jpeg": ["libjpeg", "libjpeg-turbo"],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_webp": [True, False],
        "with_heif": [True, False],
        "with_jp2": [True, False],
        "with_jxl": [True, False],
        "with_lcms2": [True, False],
        "with_lzma": [True, False],
        "with_zstd": [True, False],
        "with_zip": [True, False],
        "with_freetype": [True, False],
        "with_xml2": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "quantum_depth": 8,
        "with_jpeg": "libjpeg",
        "with_png": True,
        "with_tiff": True,
        "with_webp": True,
        "with_heif": True,
        "with_jp2": True,
        "with_jxl": True,
        "with_lcms2": True,
        "with_lzma": True,
        "with_zstd": True,
        "with_zip": True,
        "with_freetype": True,
        "with_xml2": True,
    }
    implements = ["auto_shared_fpic"]

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(
                "Windows is not supported: upstream builds it with VisualMagick (MSVC), this recipe only supports Autotools"
            )

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Core dependencies, always enabled
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("bzip2/[>=1.0.8 <2]")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/[>=9e]")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/[>=3.0.0 <4]")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_tiff:
            self.requires("libtiff/[>=4.6.0 <5]")
        if self.options.with_webp:
            self.requires("libwebp/[>=1.3.2 <2]")
        if self.options.with_heif:
            self.requires("libheif/[>=1.20 <2]")
        if self.options.with_jp2:
            self.requires("jasper/[>=4.2.0 <5]")
        if self.options.with_jxl:
            self.requires("libjxl/[>=0.11 <1]")
        if self.options.with_lcms2:
            self.requires("lcms/[>=2.16 <3]")
        if self.options.with_lzma:
            self.requires("xz_utils/[>=5.4.5 <6]")
        if self.options.with_zstd:
            self.requires("zstd/[>=1.5 <2]")
        if self.options.with_zip:
            self.requires("libzip/[>=1.10 <2]")
        if self.options.with_freetype:
            self.requires("freetype/[>=2.13 <3]")
        if self.options.with_xml2:
            self.requires("libxml2/[>=2.12.5 <3]")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        def yes_no(o):
            return "yes" if o else "no"

        tc = AutotoolsToolchain(self)
        tc.configure_args += [
            f"--with-quantum-depth={self.options.quantum_depth}",
            "--with-zlib=yes",
            "--with-bzlib=yes",
            "--with-jpeg=yes",
            f"--with-png={yes_no(self.options.with_png)}",
            f"--with-tiff={yes_no(self.options.with_tiff)}",
            f"--with-webp={yes_no(self.options.with_webp)}",
            f"--with-heif={yes_no(self.options.with_heif)}",
            f"--with-jp2={yes_no(self.options.with_jp2)}",
            f"--with-jxl={yes_no(self.options.with_jxl)}",
            f"--with-lcms2={yes_no(self.options.with_lcms2)}",
            f"--with-lzma={yes_no(self.options.with_lzma)}",
            f"--with-zstd={yes_no(self.options.with_zstd)}",
            f"--with-libzip={yes_no(self.options.with_zip)}",
            "--with-jbig=no",
            f"--with-ttf={yes_no(self.options.with_freetype)}",
            f"--with-xml={yes_no(self.options.with_xml2)}",
            # Not packaged in Conan Center, or out of scope for a headless library build.
            # Disabled explicitly so the build never links whatever is installed on the host.
            "--with-x=no",
            "--with-wmf=no",
            "--with-gs=no",
            "--with-fpx=no",
            "--with-trio=no",
            "--with-perl=no",
            "--disable-openmp",
        ]
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        pkgdeps = PkgConfigDeps(self)
        pkgdeps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(
            self,
            "Copyright.txt",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        autotools = Autotools(self)
        autotools.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*-config", os.path.join(self.package_folder, "bin"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        core_requires = ["zlib::zlib", "bzip2::bzip2"]
        core_requires.append(f"{self.options.with_jpeg}::{self.options.with_jpeg}")
        optional = {
            "with_png": "libpng::libpng",
            "with_tiff": "libtiff::libtiff",
            "with_webp": "libwebp::libwebp",
            "with_heif": "libheif::libheif",
            "with_jp2": "jasper::jasper",
            "with_jxl": "libjxl::libjxl",
            "with_lcms2": "lcms::lcms",
            "with_lzma": "xz_utils::xz_utils",
            "with_zstd": "zstd::zstd",
            "with_zip": "libzip::libzip",
            "with_freetype": "freetype::freetype",
            "with_xml2": "libxml2::libxml2",
        }
        core_requires += [
            req for opt, req in optional.items() if self.options.get_safe(opt)
        ]

        include_dir = os.path.join("include", "GraphicsMagick")

        core = self.cpp_info.components["GraphicsMagick"]
        core.set_property("pkg_config_name", "GraphicsMagick")
        core.includedirs = [include_dir]
        core.libs = ["GraphicsMagick"]
        core.requires = core_requires
        if self.settings.os in ("Linux", "FreeBSD"):
            core.system_libs = ["m", "pthread"]

        wand = self.cpp_info.components["GraphicsMagickWand"]
        wand.set_property("pkg_config_name", "GraphicsMagickWand")
        wand.includedirs = [include_dir]
        wand.libs = ["GraphicsMagickWand"]
        wand.requires = ["GraphicsMagick"]

        cxx = self.cpp_info.components["GraphicsMagick++"]
        cxx.set_property("pkg_config_name", "GraphicsMagick++")
        cxx.includedirs = [include_dir]
        cxx.libs = ["GraphicsMagick++"]
        cxx.requires = ["GraphicsMagickWand"]
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                cxx.system_libs.append(libcxx)
